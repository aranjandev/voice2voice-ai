#!/usr/bin/env bash
# ------------------------------------------------------------------
# git_ops.sh — Helper script for common GitHub operations.
# Reads GH_PAT from .env so secrets never appear in task definitions.
#
# Usage:
#   ./scripts/git_ops.sh push
#   ./scripts/git_ops.sh pull
#   ./scripts/git_ops.sh pr  "PR title" "PR body"  [base_branch]
#   ./scripts/git_ops.sh branch <branch-name>
# ------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- Load .env ----
ENV_FILE="$PROJECT_ROOT/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env file not found at $ENV_FILE" >&2
    exit 1
fi

# Source only GH_PAT (avoid polluting shell with unrelated vars)
GH_PAT="$(grep -E '^GH_PAT=' "$ENV_FILE" | head -1 | cut -d'=' -f2-)"
if [[ -z "$GH_PAT" ]]; then
    echo "ERROR: GH_PAT is not set in .env" >&2
    exit 1
fi

# ---- Ensure remote uses PAT-authenticated HTTPS URL ----
configure_remote() {
    local current_url
    current_url="$(git -C "$PROJECT_ROOT" remote get-url origin 2>/dev/null || true)"

    # Extract owner/repo from various URL formats
    local owner_repo
    if [[ "$current_url" =~ github\.com[:/](.+/.+?)(\.git)?$ ]]; then
        owner_repo="${BASH_REMATCH[1]}"
        owner_repo="${owner_repo%.git}"
    else
        echo "ERROR: Could not parse GitHub owner/repo from remote URL: $current_url" >&2
        exit 1
    fi

    # Extract the username (owner) for authentication
    local username
    username="$(echo "$owner_repo" | cut -d'/' -f1)"

    local authenticated_url="https://${username}:${GH_PAT}@github.com/${owner_repo}.git"
    if [[ "$current_url" != "$authenticated_url" ]]; then
        git -C "$PROJECT_ROOT" remote set-url origin "$authenticated_url"
        echo "Remote URL updated to use PAT authentication."
    fi
}

# ---- Helpers ----
current_branch() {
    git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD
}

repo_owner_name() {
    local url
    url="$(git -C "$PROJECT_ROOT" remote get-url origin)"
    if [[ "$url" =~ github\.com[:/](.+/.+?)(\.git)?$ ]]; then
        echo "${BASH_REMATCH[1]}" | sed 's/\.git$//'
    fi
}

# ---- Commands ----
cmd_push() {
    configure_remote
    local branch
    branch="$(current_branch)"
    echo "Pushing branch '$branch' to origin..."
    git -C "$PROJECT_ROOT" push -u origin "$branch"
    echo "Push complete."
}

cmd_pull() {
    configure_remote
    local branch
    branch="$(current_branch)"
    echo "Pulling latest for branch '$branch'..."
    git -C "$PROJECT_ROOT" pull origin "$branch"
    echo "Pull complete."
}

cmd_pr() {
    local title="${1:?Usage: git_ops.sh pr \"title\" \"body\" [base_branch]}"
    local body="${2:-}"
    local base="${3:-main}"
    local head
    head="$(current_branch)"
    local repo
    repo="$(repo_owner_name)"

    if [[ -z "$repo" ]]; then
        echo "ERROR: Could not determine GitHub owner/repo." >&2
        exit 1
    fi

    if [[ "$head" == "$base" ]]; then
        echo "ERROR: Current branch '$head' is the same as base '$base'. Switch to a feature branch first." >&2
        exit 1
    fi

    # Push first to make sure remote has the latest
    cmd_push

    echo ""
    echo "Creating PR: '$title'"
    echo "  head: $head → base: $base"
    echo "  repo: $repo"
    echo ""

    local response
    response="$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $GH_PAT" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/repos/${repo}/pulls" \
        -d "$(jq -n \
            --arg title "$title" \
            --arg body "$body" \
            --arg head "$head" \
            --arg base "$base" \
            '{title: $title, body: $body, head: $head, base: $base}'
        )")"

    local http_code
    http_code="$(echo "$response" | tail -1)"
    local json_body
    json_body="$(echo "$response" | sed '$d')"

    if [[ "$http_code" == "201" ]]; then
        local pr_url
        pr_url="$(echo "$json_body" | jq -r '.html_url')"
        echo "PR created successfully: $pr_url"
    else
        echo "ERROR: Failed to create PR (HTTP $http_code)" >&2
        echo "$json_body" | jq -r '.message // .errors // .' 2>/dev/null || echo "$json_body"
        exit 1
    fi
}

cmd_branch() {
    local branch_name="${1:?Usage: git_ops.sh branch <branch-name>}"
    echo "Creating and switching to branch '$branch_name'..."
    git -C "$PROJECT_ROOT" checkout -b "$branch_name"
    echo "Switched to new branch '$branch_name'."
}

# ---- Dispatcher ----
ACTION="${1:-}"
shift || true

case "$ACTION" in
    push)   cmd_push "$@" ;;
    pull)   cmd_pull "$@" ;;
    pr)     cmd_pr "$@" ;;
    branch) cmd_branch "$@" ;;
    *)
        echo "Usage: git_ops.sh {push|pull|pr|branch} [args...]" >&2
        echo ""
        echo "Commands:"
        echo "  push                          Push current branch to origin"
        echo "  pull                          Pull latest from origin for current branch"
        echo "  pr \"title\" \"body\" [base]       Create a pull request (default base: main)"
        echo "  branch <name>                 Create and switch to a new branch"
        exit 1
        ;;
esac
