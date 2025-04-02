from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from apps.data_processing.models import CaseMetadata

# Create your models here.

class Category(models.Model):
    """Model to store unique categories from case metadata."""
    name = models.CharField(max_length=255, unique=True)
    case_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.case_count} cases)"

    @classmethod
    def update_categories(cls):
        """
        Update categories from all cases in the database.
        Creates new categories and updates case counts.
        """
        # Get all unique categories from cases
        all_categories = set()
        for case in CaseMetadata.objects.all():
            if case.categories:  # Check if categories is not None
                all_categories.update(case.categories)
        
        # Create or update category objects
        for category_name in all_categories:
            category, created = cls.objects.get_or_create(name=category_name)
            # Update case count using PostgreSQL's @> operator for array containment
            case_count = CaseMetadata.objects.filter(categories__contains=[category_name]).count()
            if category.case_count != case_count:
                category.case_count = case_count
                category.save()
        
        # Remove categories that no longer have any cases
        cls.objects.filter(case_count=0).delete()

@receiver(post_save, sender=CaseMetadata)
def update_categories_on_case_save(sender, instance, **kwargs):
    """
    Signal handler to update categories when a case is saved.
    This ensures categories are always up to date when new cases are added.
    """
    Category.update_categories()
