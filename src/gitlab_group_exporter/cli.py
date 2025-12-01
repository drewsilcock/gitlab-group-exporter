import time
import typing as t
from datetime import datetime
from pathlib import Path

import typer
from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError
from gitlab.v4.objects import Group, Project
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from .settings import Settings

cli = typer.Typer()
console = Console()


def get_gitlab_client(url: str, token: str) -> Gitlab:
    """Initialize GitLab client."""
    return Gitlab(url, private_token=token)


def export_group(group: Group, output_dir: Path, gl: Gitlab) -> None:
    group_export = group.exports.create()

    with Progress() as progress:
        task_id = progress.add_task("Downloading group export", total=None)

        with open(output_dir / f"{group.name}.tar.gz", "wb") as fp:

            def write_chunk(chunk: bytes) -> None:
                fp.write(chunk)
                progress.update(task_id, advance=len(chunk))

            while True:
                try:
                    group_export.download(streamed=True, action=write_chunk)
                    break
                except GitlabGetError:
                    pass

            time.sleep(1)

    console.log(f"Exported group {group.name} to {output_dir / f'{group.name}.tar.gz'}")


def export_project(project_id: str, output_dir: Path, gl: Gitlab) -> Project:
    project = gl.projects.get(project_id)

    project_export = project.exports.create()
    project_export.refresh()

    with Progress() as progress:
        task_id = progress.add_task("Waiting for project export to complete", total=None)

        while project_export.export_status != "finished":
            project_export.refresh()
            time.sleep(1)

        progress.stop_task(task_id)

        task_id = progress.add_task("Downloading project export")

        with open(output_dir / f"{project.name}.tar.gz", "wb") as fp:

            def write_chunk(chunk: bytes) -> None:
                fp.write(chunk)
                progress.advance(task_id, advance=len(chunk))

            project_export.download(streamed=True, action=write_chunk)

    console.log(f"Exported project {project.name} to {output_dir / f'{project.name}.tar.gz'}")
    return project


@cli.command()
def main(
    group_name: t.Annotated[str, typer.Argument(help="GitLab group name")],
    output_dir: t.Annotated[
        Path | None,
        typer.Option(
            "--output-dir", "-o", help="Folder to put exports in (default: 'export-{group_name}-{current date}')."
        ),
    ] = None,
    server_url: t.Annotated[
        str | None,
        typer.Option(
            help="GitLab instance base URL – falls back to SERVER_URL env var which falls back to https://gitlab.com."
        ),
    ] = None,
    token: t.Annotated[
        str | None,
        typer.Option(
            "--token",
            "-t",
            help="GitLab private token – falls back to GITLAB_PRIVATE_TOKEN env var.",
        ),
    ] = None,
) -> None:
    """Export all projects from a GitLab group to JSON."""

    settings = Settings()

    token = token or settings.gitlab_private_token.get_secret_value()
    if not token:
        console.print("[red]Error: No GitLab token provided. Use --token or GITLAB_PRIVATE_TOKEN env var[/red]")
        raise typer.Exit(1)

    server_url = server_url or settings.server_url

    # Set default output filename
    if output_dir is None:
        group_name_safe = group_name.replace("/", "-")
        output_dir = Path(f"./export-{group_name_safe}-{datetime.now().strftime('%Y-%m-%d')}")

    output_dir.mkdir(exist_ok=True, parents=True)

    try:
        gl = get_gitlab_client(server_url, token)
        console.log("Getting user")
        gl.auth()  # Validate token
        console.log("Got user")
    except GitlabAuthenticationError as e:
        console.print(f"[red]Error: Invalid GitLab token: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error connecting to GitLab: {e}[/red]")
        raise typer.Exit(1) from e

    current_user = gl.user
    if current_user is None:
        raise ValueError("Failed to retrieve current user information")

    console.print(f"[green]Authenticated to {server_url} as {current_user.username}[/green]")

    console.print(f"[blue]Exporting projects from group:[/blue] {group_name}")

    group = gl.groups.get(group_name)

    export_group(group, output_dir, gl)

    group_projects = group.projects.list(get_all=True)
    projects: list[Project] = []
    for group_project in group_projects:
        projects.append(export_project(group_project.id, output_dir, gl))

    # Display results
    table = Table(title=f"Exported {len(projects)} Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="magenta")
    table.add_column("Visibility", style="green")
    table.add_column("URL", style="blue")

    for proj in projects:
        table.add_row(proj.name, proj.path, proj.visibility, proj.url)

    console.print(table)
    console.print(f"\n[green]✓ Exported to:[/green] {output_dir.absolute()}")
