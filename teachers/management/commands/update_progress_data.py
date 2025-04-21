# teachers/management/commands/update_progress_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from teachers.models import Teacher, PeriodProgress, TopicCompletion
from academics.models import AcademicYear, GradeLevel, Periodo, Paralelo
from teachers.utils import get_pygsheets_client, find_valid_teacher_worksheets, extract_worksheet_data, extract_sheet_key_from_url
from django.conf import settings


SERVICE_ACCOUNT_FILE = settings.SERVICE_ACCOUNT_FILE  # Ensure this is set in your settings.py

class Command(BaseCommand):
    help = 'Fetches progress data from teacher Google Sheets and updates the database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting data update process...")
        active_teachers = Teacher.objects.filter(is_active=True)
        # Assuming you want to process for the currently active academic year
        try:
             # You might need a way to determine the 'current' year or pass it as an argument
             current_academic_year = AcademicYear.objects.get(is_active=True)
        except AcademicYear.DoesNotExist:
             self.stderr.write(self.style.ERROR("No active AcademicYear found. Cannot proceed."))
             return
        except AcademicYear.MultipleObjectsReturned:
             self.stderr.write(self.style.ERROR("Multiple active AcademicYears found. Define only one."))
             return


        # Pre-fetch lookup objects for efficiency if feasible, or fetch as needed
        # grade_levels = {g.code: g for g in GradeLevel.objects.all()}
        # periodos = {p.number: p for p in Periodo.objects.filter(trimestre__academic_year=current_academic_year)}
        # paralelos = {p.code: p for p in Paralelo.objects.all()}

        gc = get_pygsheets_client(SERVICE_ACCOUNT_FILE) # Authorize once

        for teacher in active_teachers:
            self.stdout.write(f"Processing teacher: {teacher.full_name}...")
            try:
                # 1. Find valid worksheets
                valid_titles = find_valid_teacher_worksheets(
                    teacher.google_sheet_url, SERVICE_ACCOUNT_FILE # Pass client 'gc' instead? Refactor needed.
                )
                if not valid_titles:
                    self.stdout.write(f"  No valid worksheets found for {teacher.full_name}.")
                    continue

                sh = gc.open_by_key(extract_sheet_key_from_url(teacher.google_sheet_url)) # Need key extraction here too

                # 2. Extract data from each valid worksheet
                for title in valid_titles:
                    self.stdout.write(f"  Processing worksheet: {title}...")
                    try:
                        wks = sh.worksheet_by_title(title)
                        extracted_data = extract_worksheet_data(wks)

                        # 3. Update/Create database records using extracted data
                        now = timezone.now()

                        # Process Period Progress
                        for record in extracted_data.get('period_progress', []):
                            try:
                                # Fetch related objects (can be optimized)
                                grade_level_obj = GradeLevel.objects.get(code=record['grade_level'])
                                periodo_obj = Periodo.objects.get(trimestre__academic_year=current_academic_year, number=record['periodo'])
                                paralelo_obj = Paralelo.objects.get(code=record['paralelo'])

                                PeriodProgress.objects.update_or_create(
                                    teacher=teacher,
                                    academic_year=current_academic_year,
                                    grade_level=grade_level_obj,
                                    periodo=periodo_obj,
                                    paralelo=paralelo_obj,
                                    defaults={
                                        'progress_percentage': record['progress_percentage'],
                                        'last_updated': now
                                    }
                                )
                            except (GradeLevel.DoesNotExist, Periodo.DoesNotExist, Paralelo.DoesNotExist) as lookup_e:
                                 self.stderr.write(self.style.ERROR(f"    Lookup Error for Period Progress ({record}): {lookup_e}"))
                            except Exception as db_e:
                                 self.stderr.write(self.style.ERROR(f"    DB Error saving Period Progress ({record}): {db_e}"))


                        # Process Topic Completion
                        for record in extracted_data.get('topic_completion', []):
                            try:
                                grade_level_obj = GradeLevel.objects.get(code=record['grade_level'])
                                periodo_obj = Periodo.objects.get(trimestre__academic_year=current_academic_year, number=record['periodo'])
                                paralelo_obj = Paralelo.objects.get(code=record['paralelo'])
                                # Subject lookup if you add it

                                TopicCompletion.objects.update_or_create(
                                    teacher=teacher,
                                    academic_year=current_academic_year,
                                    grade_level=grade_level_obj,
                                    periodo=periodo_obj,
                                    paralelo=paralelo_obj,
                                    tema_number=record['tema_number'],
                                    # Uniqueness might need refinement if title changes but number stays same
                                    # For now, assuming unique_together in model handles this
                                    defaults={
                                        'tema_title': record['tema_title'],
                                        'completion_date': record['completion_date'],
                                        'last_updated': now
                                    }
                                )
                            except (GradeLevel.DoesNotExist, Periodo.DoesNotExist, Paralelo.DoesNotExist) as lookup_e:
                                 self.stderr.write(self.style.ERROR(f"    Lookup Error for Topic Completion ({record}): {lookup_e}"))
                            except Exception as db_e:
                                 self.stderr.write(self.style.ERROR(f"    DB Error saving Topic Completion ({record}): {db_e}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"  Failed processing worksheet '{title}' for teacher {teacher.full_name}: {e}"))

            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"Failed processing teacher {teacher.full_name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Data update process finished."))
