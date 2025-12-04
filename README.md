# GitLab Group Export CLI

Ever have to export a group and all the projects inside that group from GitLab and are fed up with how long it takes to do manually? I have, and I got bored of doing it.

This script automates the process. You give it a group and it exports the group and all the projects within that groups, and puts all the tar.gz files into a nice neat folder for handover.

## Getting Started

I wrote it using Python 3.12 – it probably works with 3.10+.

Oh, and you need [uv](https://docs.astral.sh/uv/).

```bash
uv run gitlab-export-group my-group --server-url https://gitlab.example.com
```

## Configuration

The CLI expects the group name. You can also pass in the server URL and GitLab private token into the CLI, where it will take precedence over the environment variables.

The following environment variables are supported:

- `PRIVATE_TOKEN`: Your GitLab private token.
- `SERVER_URL`: The URL of your GitLab instance.

You can put them in a `.env` file.

## Authentication

The script uses a private token for authentication – this can be a Personal Access Token (PAT) or group token. It can't be a project token because then we couldn't export the group.

For details on creating a PAT, see: https://docs.gitlab.com/user/profile/personal_access_tokens/#create-a-personal-access-token

For details on creating a group token, see: https://docs.gitlab.com/ee/user/group/settings/group_access_tokens.html#create-a-group-access-token

The token needs to have `api`, `read_api` and `read_user` scopes.
