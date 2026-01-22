"""Lambda handler for database migrations."""

import json
import subprocess
import sys


def handler(event, context):
    """Run alembic migrations.

    Args:
        event: Lambda event with optional 'revision' (default: 'head')
        context: Lambda context

    Returns:
        dict with statusCode and migration output
    """
    revision = event.get("revision", "head")

    try:
        result = subprocess.run(
            ["alembic", "upgrade", revision],
            capture_output=True,
            text=True,
            check=True,
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "revision": revision,
                "output": result.stdout,
            }),
        }
    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "revision": revision,
                "error": e.stderr,
                "output": e.stdout,
            }),
        }
