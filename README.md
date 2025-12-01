# GitLab Group Export CLI

Export all projects from a GitLab group to a JSON file.

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/):

```bash
uv run gitlab-export.py mygroup
```

## Usage

```bash
# Export to group_name.json
uv run gitlab-export.py mygroup

# Specify output file
uv run gitlab-export.py mygroup --output projects.json

# Use a different GitLab instance
uv run gitlab-export.py mygroup --url https://gitlab.example.com
```

## Authentication

The script uses a GitLab personal access token for authentication.

### Generate a Token

1. Go to your GitLab instance (e.g., https://gitlab.com)
2. Click your profile icon → **Settings** → **Access Tokens**
3. Create a new token with at least the `api` and `read_api` scopes
4. Copy the token

### Provide the Token

Pass it as an option:
```bash
uv run gitlab-export.py mygroup --token glpat-xxx
```

Or set it as an environment variable:
```bash
export GITLAB_PRIVATE_TOKEN=glpat-xxx
uv run gitlab-export.py mygroup
```

## Output

The script exports a JSON file containing:
- Project name, path, and full path with namespace
- Project URL and visibility (public/private)
- Description and creation/activity timestamps

Projects are displayed in a table before export completes.
