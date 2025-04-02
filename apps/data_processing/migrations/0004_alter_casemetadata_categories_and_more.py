# Generated by Django 5.1.7 on 2025-03-27 22:41

from django.db import migrations
from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField

class Migration(migrations.Migration):

    dependencies = [
        ('data_processing', '0003_casemetadata_source_url_and_more'),
    ]

    operations = [
        # Add new array fields
        migrations.AddField(
            model_name='casemetadata',
            name='categories_new',
            field=ArrayField(base_field=CharField(max_length=255), blank=True, null=True),
        ),
        migrations.AddField(
            model_name='casemetadata',
            name='keywords_new',
            field=ArrayField(base_field=CharField(max_length=255), blank=True, null=True),
        ),
        migrations.AddField(
            model_name='factpattern',
            name='canlii_categories_new',
            field=ArrayField(base_field=CharField(max_length=255), blank=True, null=True),
        ),
        migrations.AddField(
            model_name='factpattern',
            name='canlii_keywords_new',
            field=ArrayField(base_field=CharField(max_length=255), blank=True, null=True),
        ),
        # Run SQL to copy data
        migrations.RunSQL(
            sql="""
            UPDATE data_processing_casemetadata 
            SET categories_new = ARRAY(
                SELECT jsonb_array_elements_text(categories)
                WHERE categories IS NOT NULL AND jsonb_typeof(categories) = 'array'
            ),
            keywords_new = ARRAY(
                SELECT jsonb_array_elements_text(keywords)
                WHERE keywords IS NOT NULL AND jsonb_typeof(keywords) = 'array'
            );
            
            UPDATE data_processing_factpattern
            SET canlii_categories_new = ARRAY(
                SELECT jsonb_array_elements_text(canlii_categories)
                WHERE canlii_categories IS NOT NULL AND jsonb_typeof(canlii_categories) = 'array'
            ),
            canlii_keywords_new = ARRAY(
                SELECT jsonb_array_elements_text(canlii_keywords)
                WHERE canlii_keywords IS NOT NULL AND jsonb_typeof(canlii_keywords) = 'array'
            );
            """,
            reverse_sql="""
            UPDATE data_processing_casemetadata 
            SET categories = to_jsonb(categories_new),
                keywords = to_jsonb(keywords_new);
                
            UPDATE data_processing_factpattern
            SET canlii_categories = to_jsonb(canlii_categories_new),
                canlii_keywords = to_jsonb(canlii_keywords_new);
            """
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='casemetadata',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='casemetadata',
            name='keywords',
        ),
        migrations.RemoveField(
            model_name='factpattern',
            name='canlii_categories',
        ),
        migrations.RemoveField(
            model_name='factpattern',
            name='canlii_keywords',
        ),
        # Rename new fields
        migrations.RenameField(
            model_name='casemetadata',
            old_name='categories_new',
            new_name='categories',
        ),
        migrations.RenameField(
            model_name='casemetadata',
            old_name='keywords_new',
            new_name='keywords',
        ),
        migrations.RenameField(
            model_name='factpattern',
            old_name='canlii_categories_new',
            new_name='canlii_categories',
        ),
        migrations.RenameField(
            model_name='factpattern',
            old_name='canlii_keywords_new',
            new_name='canlii_keywords',
        ),
    ]
