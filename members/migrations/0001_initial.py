# Generated by Django 3.2.5 on 2021-12-29 14:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member_Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reviewed', models.DateTimeField(default=django.utils.timezone.now)),
                ('loan_amount', models.PositiveBigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Member_Repayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_repaid', models.PositiveBigIntegerField()),
                ('date_repaid', models.DateTimeField(default=django.utils.timezone.now)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member_loan')),
            ],
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=30)),
                ('spouse_first_name', models.CharField(max_length=30)),
                ('spouse_last_name', models.CharField(max_length=30)),
                ('spouse_number', models.CharField(max_length=30)),
                ('home_address', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Loan_Balance',
            fields=[
                ('loan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='members.member_loan')),
                ('interest', models.PositiveBigIntegerField()),
                ('lb_balance', models.PositiveBigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Member_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mr_date_requested', models.DateTimeField(default=django.utils.timezone.now)),
                ('mr_amount_requested', models.PositiveBigIntegerField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.members')),
            ],
        ),
        migrations.AddField(
            model_name='member_loan',
            name='member_request',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='members.member_request'),
        ),
        migrations.CreateModel(
            name='Unpaid',
            fields=[
                ('outsider_repayment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='members.member_repayment')),
                ('balance', models.PositiveBigIntegerField(blank=True)),
                ('loan_interest', models.PositiveBigIntegerField()),
                ('outsider_loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member_loan')),
            ],
        ),
    ]
