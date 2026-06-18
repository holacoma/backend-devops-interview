#!/bin/bash
set -e

echo "Running migrations..."
uv run python manage.py migrate

USER_COUNT=$(uv run python manage.py shell -c "from blog.models import User; print(User.objects.count())")
TAG_COUNT=$(uv run python manage.py shell -c "from blog.models import Tag; print(Tag.objects.count())")
POST_COUNT=$(uv run python manage.py shell -c "from blog.models import Post; print(Post.objects.count())")
COMMENT_COUNT=$(uv run python manage.py shell -c "from blog.models import Comment; print(Comment.objects.count())")

if [ "$USER_COUNT" -eq "0" ] || [ "$TAG_COUNT" -eq "0" ] || [ "$POST_COUNT" -eq "0" ] || [ "$COMMENT_COUNT" -eq "0" ]; then
    echo ""
    echo "Missing data detected:"
    echo "  Users:    $USER_COUNT"
    echo "  Tags:     $TAG_COUNT"
    echo "  Posts:    $POST_COUNT"
    echo "  Comments: $COMMENT_COUNT"
    echo ""
    read -p "Seed the database? [y/N] " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        uv run python manage.py seed --scale "${SEED_SCALE:-0.1}"
    fi
fi

exec uv run python manage.py runserver 0.0.0.0:8000
