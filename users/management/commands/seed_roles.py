from __future__ import annotations

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from teams.models import Team, TeamMember
from projects.models import Project, ProjectMember

User = get_user_model()


def _get_env(key, default):
    return os.environ.get(key, default)


class Command(BaseCommand):
    help = "Seed development users, teams and projects with roles"

    def handle(self, *args, **options):
        # Create superuser
        super_email = _get_env("SUPERUSER_EMAIL", "super@example.com")
        super_pass = _get_env("SUPERUSER_PASSWORD", "superPass123!")
        if not User.objects.filter(email=super_email).exists():
            print(f"Creating superuser: {super_email}")
            User.objects.create_superuser(email=super_email, password=super_pass)
        else:
            print(f"Superuser {super_email} already exists")

        # Create general user accounts
        users = [
            ("OWNER_EMAIL", "OWNER_PASSWORD"),
            ("ADMIN_EMAIL", "ADMIN_PASSWORD"),
            ("MEMBER_EMAIL", "MEMBER_PASSWORD"),
            ("VIEWER_EMAIL", "VIEWER_PASSWORD"),
            ("PROJECT_MANAGER_EMAIL", "PROJECT_MANAGER_PASSWORD"),
            ("PROJECT_MEMBER_EMAIL", "PROJECT_MEMBER_PASSWORD"),
        ]
        created_users = {}
        for email_var, pw_var in users:
            email = _get_env(email_var, f"{email_var.lower()}@example.com")
            password = _get_env(pw_var, "password123!")
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.set_password(password)
                user.save()
                print(f"Created user: {email}")
            else:
                print(f"User exists: {email}")
            created_users[email_var] = user

        # Create demo team
        team, created = Team.objects.get_or_create(name="Demo Team", defaults={"created_by": created_users["OWNER_EMAIL"]})
        if created:
            print("Created Demo Team")
        else:
            print("Demo Team already exists")

        # Ensure team members
        def add_team_member_by_env(env_email_var, role):
            user = created_users.get(env_email_var)
            if not user:
                print(f"Skipping {env_email_var}; not found")
                return
            membership, created = TeamMember.objects.get_or_create(team=team, user=user, defaults={"role": role})
            if not created and membership.role != role:
                membership.role = role
                membership.save(update_fields=["role"])
            print(f"Team member: {user.email} -> {role}")

        add_team_member_by_env("OWNER_EMAIL", TeamMember.RoleChoices.OWNER)
        add_team_member_by_env("ADMIN_EMAIL", TeamMember.RoleChoices.ADMIN)
        add_team_member_by_env("MEMBER_EMAIL", TeamMember.RoleChoices.MEMBER)
        add_team_member_by_env("VIEWER_EMAIL", TeamMember.RoleChoices.VIEWER)

        # Create demo project
        project, created = Project.objects.get_or_create(team=team, name="Demo Project", defaults={"description": "Seeded project for local dev"})
        if created:
            print("Created Demo Project")
        else:
            print("Demo Project already exists")

        # Ensure project memberships
        def add_project_member_by_env(env_email_var, role):
            user = created_users.get(env_email_var)
            if not user:
                print(f"Skipping {env_email_var}; not found")
                return
            membership, created = ProjectMember.objects.get_or_create(project=project, user=user, defaults={"role": role})
            if not created and membership.role != role:
                membership.role = role
                membership.save(update_fields=["role"])
            print(f"Project member: {user.email} -> {role}")

        add_project_member_by_env("PROJECT_MANAGER_EMAIL", ProjectMember.RoleChoices.MANAGER)
        add_project_member_by_env("PROJECT_MEMBER_EMAIL", ProjectMember.RoleChoices.MEMBER)

        print("Seeding complete.")
