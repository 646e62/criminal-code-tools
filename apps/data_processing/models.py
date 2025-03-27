from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class CaseMetadata(models.Model):
    case_id = models.CharField(max_length=100, unique=True)
    style_of_cause = models.CharField(max_length=1024)
    citation = models.CharField(max_length=255)

    class CitationType(models.TextChoices):
        NEUTRAL = 'neutral', _('Neutral')
        CANLII = 'canlii', _('CanLII')
        OTHER = 'other', _('Other')

    citation_type = models.CharField(
        max_length=20,
        choices=CitationType.choices,
        default=CitationType.NEUTRAL
    )

    official_reporter_citation = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=4)  
    court = models.CharField(max_length=20)
    decision_number = models.CharField(max_length=20, blank=True, null=True)  
    jurisdiction = models.CharField(max_length=100)
    court_name = models.CharField(max_length=255, blank=True, null=True)  
    court_level = models.CharField(max_length=100, blank=True, null=True)  
    source_url = models.URLField(blank=True, null=True)  
    short_url = models.URLField(blank=True, null=True)  
    language = models.CharField(max_length=50)
    docket_number = models.CharField(max_length=100, blank=True, null=True)  
    decision_date = models.DateTimeField(null=True, blank=True)  
    keywords = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    categories = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    cited_cases = models.JSONField(blank=True, default=list)
    citing_cases = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-decision_date', 'case_id']

    def __str__(self):
        return f"{self.style_of_cause} ({self.citation})"

class FactPattern(models.Model):
    case = models.OneToOneField(CaseMetadata, on_delete=models.CASCADE, primary_key=True)

    canlii_keywords = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    canlii_categories = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    local_categories = models.JSONField(blank=True, default=list)
    canlii_ai_summary = models.JSONField(blank=True, null=True)
    local_ai_summary = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Fact pattern for case {self.case.case_id}"

class SentencingRange(models.Model):
    uid = models.CharField(max_length=255, unique=True)
    case = models.ForeignKey(CaseMetadata, on_delete=models.CASCADE)
    section = models.CharField(max_length=50)
    offender = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    jail = models.TextField(blank=True)
    mode = models.CharField(max_length=255, blank=True)
    conditions = models.TextField(blank=True)
    fine = models.CharField(max_length=100, blank=True)
    appeal = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', 'section']

    def __str__(self):
        return f"SentencingRange ({self.uid})"

class Offence(models.Model):
    section = models.CharField(max_length=50, unique=True)
    offence_name = models.CharField(max_length=255)

    minimum_summary = models.TextField()
    maximum_summary = models.TextField()
    minimum_indictable = models.TextField()
    maximum_indictable = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['section']

    def __str__(self):
        return f"{self.section}: {self.offence_name}"
