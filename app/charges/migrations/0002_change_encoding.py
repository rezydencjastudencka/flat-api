# Generated by Django 2.0.1 on 2018-02-14 20:15

from django.db import migrations


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != 'mysql':
        return

    with schema_editor.connection.cursor() as cursor:
        print('')
        print('    Altering database ...')
        cursor.execute("ALTER DATABASE CHARACTER SET utf8 COLLATE utf8_bin;")
        cursor.execute("SHOW TABLES;")
        for table, in cursor.fetchall():
            print('    Altering table %s ...' % table)
            cursor.execute(
                "ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE utf8_bin" % table
            )


def backwards(self, orm):
    # Altering the tables takes lots of time and
    # locks the tables, since it copies all the data.
    raise RuntimeError(
        "This migration probably took 2 hours, you don't really want to rollback ..."
    )


class Migration(migrations.Migration):
    dependencies = [
        ('charges', '0001_initial'),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
