import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from blog.models import Comment, Post, Tag, User

from .seeders.comments import seed_comments
from .seeders.posts import attach_post_tags, seed_posts
from .seeders.tags import seed_tags
from .seeders.users import seed_users
from .seeders.utils import power_law_weights

NUM_USERS = 1000
NUM_TAGS = 50
NUM_POSTS = 100_000
NUM_COMMENTS = 500_000
TAGS_PER_POST_AVG = 3
BATCH = 1000


class Command(BaseCommand):
    help = "Seed the database with users, tags, posts, and comments."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Seed even if data exists")
        parser.add_argument("--purge", action="store_true", help="Delete all existing data before seeding")
        parser.add_argument(
            "--scale",
            type=float,
            default=1.0,
            help="Fraction of the full dataset to seed (e.g. 0.01 = 1%%). Default: 1.0",
        )

    def handle(self, *args, **opts):
        if opts["purge"]:
            self.stdout.write("Purging existing data...")
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            User.objects.all().delete()

        if User.objects.exists() and not opts["force"]:
            self.stdout.write("Database already has users; pass --force to seed anyway.")
            return

        scale = opts["scale"]
        num_users = max(1, int(NUM_USERS * scale))
        num_tags = max(6, int(NUM_TAGS * scale))
        num_posts = max(1, int(NUM_POSTS * scale))
        num_comments = max(1, int(NUM_COMMENTS * scale))

        fake = Faker()
        Faker.seed(42)
        random.seed(42)

        now = timezone.now()
        three_years_ago = now - timedelta(days=365 * 3)

        self.stdout.write(f"Seeding users... (scale={scale})")
        user_ids = seed_users(fake, now, three_years_ago, num_users, BATCH)

        self.stdout.write("Seeding tags...")
        hot_tag_ids, cold_tag_ids = seed_tags(fake, now, num_tags, BATCH)

        author_weights = power_law_weights(len(user_ids), top_n=10, top_share=0.3)

        self.stdout.write(f"Seeding {num_posts} posts...")
        post_ids = seed_posts(fake, user_ids, author_weights, now, three_years_ago, num_posts, BATCH)

        self.stdout.write("Attaching tags to posts...")
        attach_post_tags(post_ids, hot_tag_ids, cold_tag_ids, TAGS_PER_POST_AVG, BATCH)

        self.stdout.write(f"Seeding {num_comments} comments...")
        seed_comments(fake, post_ids, user_ids, author_weights, now, three_years_ago, num_comments, BATCH)

        self.stdout.write(self.style.SUCCESS("Done."))
