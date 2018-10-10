using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Arbiter
{
    // Результат проверки
    public class Result
    {
        public string CompilationResult;  // Результат компиляции
        public Dictionary<string, string> PreliminaryTestsResults;  // Результаты проверки на предварительных тестах
        public Dictionary<string, Dictionary<string, string>> SubtasksResults;  // Результаты проверки на подзадачах
        public int Total;  // Общий балл
    }

    // Отправка
    public class Submission
    {
        public int Attempt;  // Номер попытки
        public DateTime SubmissionTime;  // Дата и время отправки
        public string User;  // Пользователь
        public string Problem;  // Код задачи
        public string Language;  // Код языка программирования
        public Result Result;  // Результат проверки
        public string Source;  // Исходный код решения

        public bool Save(string fileName, Object submission)
        {
            //    var serializer = new SerializerBuilder()
            //        .WithNamingConvention(new UnderscoredNamingConvention())
            //        .EmitDefaults()
            //        .Build();
            //    File.WriteAllText(fileName, serializer.Serialize(submission));
            return true;
        }

        public static Submission Load(string fileName)
        {
            var content = File.ReadAllText(fileName);
            return Arbiter.GetDeserializer().Deserialize<Submission>(content);
        }
    }


    // Арбитр
    public class Arbiter
    {
        static bool UserWantsToStop;

        readonly string LanguagesDir;
        readonly string QueueDir;
        readonly string ResultsDir;
        readonly string WorkDir;

        public Dictionary<string, Language> languages;
        public Dictionary<string, Problem> problems;
        public DateTime LanguagesModificationTime;

        internal Dictionary<string, Language> Languages { get => languages; set => languages = value; }
        internal Dictionary<string, Problem> Problems { get => problems; set => problems = value; }

        public static Deserializer GetDeserializer()
        {
            return new DeserializerBuilder()
                .WithNamingConvention(new UnderscoredNamingConvention())
                .Build();
        }

        // Обход файлов в очереди
        public bool QueueIsEmpty()
        {
            var Empty = true;  // Нужно, чтобы определить можно ли поспать или нет
            var queue = Directory.GetFiles(QueueDir, "*.yaml");
            foreach (var fileName in queue)  // fileName включает в себя имя каталога
            {
                Empty = false;  // Блин, не получиться поспать

                // Переместим файл, чтобы в следующий раз не обработать его повторно
                //        var newFileName = fileName.Replace(QueueDir, ResultsDir);
                //        File.Move(fileName, newFileName);

                // Читаем и проверяем файл
                //        var submission = DeserializeSubmission(newFileName);
                //        submission.Result = new Result();
                //        var language = Languages[submission.Language];
                //        if (Compilation(language, submission.Source) == "OK")
                //        {
                //            var problem = Problems[submission.Problem];
                //            //if (PreliminaryTestsCheck(language, problem, submission) == "OK")
                //            //{
                //            //    var total = 0;
                //            //    foreach (KeyValuePair<string, Subtask> entry in problem.Subtasks)
                //            //    {
                //            //        SubtaskCheck(submission, language, entry.Value);
                //            //    }
                //            //    submission.Result.Total = total;
                //            //}
                //        }

                //        Serialize(newFileName, submission);
            }
            return Empty;
        }

        // Если задачи изменились, надо их обновить
        public bool ProblemsAreUnchanged()
        {
            var Unchanged = true;

            // Проверим, что ранее загруженные задачи не изменились
            string[] codes = new string[Problems.Count];
            Problems.Keys.CopyTo(codes, 0);
            foreach (var code in codes)
            {
                var problem = Problems[code];
                var filename = WorkDir + '\\' + code + '\\' + "problem.yaml";

                // Если задача была удалена
                if (!File.Exists(filename))
                {
                    Unchanged = false;
                    Problems.Remove(code);
                    Logger.Message("Problem {} was removed", code);
                    continue;
                }

                // Если задача была изменена
                var mtime = File.GetLastWriteTime(filename);
                if (mtime > problem.ModificationTime)
                {
                    Unchanged = false;
                    Logger.Message("Problem {} change detected", code);
                    problem = Problem.Load(filename);
                    if (problem != null && problem.Check())
                    {
                        problem.ModificationTime = mtime;
                        Problems[code] = problem;
                        Logger.Message("Problem {} successfully checked. Changes are committed.", code);
                    }
                    else
                    {
                        Problems.Remove(code);
                        Logger.Message("Problem {} check failed. Problem was removed.", code);
                    }
                }
            }

            // Поиск новых задач в рабочем каталоге
            var dirnames = Directory.GetDirectories(WorkDir);
            foreach (var dirname in dirnames)
            {
                // Пропускаем служебные каталоги
                if (IsServiceDirectory(dirname))
                    continue;

                // Пропускаем каталоги без описания задачи
                var filename = dirname + "\\problem.yaml";
                if (!File.Exists(filename))
                    continue;

                // Пропускаем уже загруженные задачи
                var code = dirname.Substring(dirname.LastIndexOf('\\') + 1);
                if (Problems.ContainsKey(code))
                    continue;

                Logger.Message("New problem {} has been found", code);
                var problem = Problem.Load(dirname);
                if (problem != null && problem.Check())
                {
                    Unchanged = false;
                    problem.ModificationTime = File.GetLastWriteTime(filename);
                    Problems[code] = problem;
                    Logger.Message("Problem {} successfully checked. Changes are committed.", code);
                }
                else
                {
                    Logger.Message("Problem {} check failed. Changes are ignored.", code);
                }
            }

            return Unchanged;
        }

        bool IsServiceDirectory(string dirname)
        {
            return string.Equals(dirname, LanguagesDir, StringComparison.OrdinalIgnoreCase)
                || string.Equals(dirname, QueueDir, StringComparison.OrdinalIgnoreCase)
                || string.Equals(dirname, ResultsDir, StringComparison.OrdinalIgnoreCase);
        }

        // Если языки программирования изменились, надо их обновить
        bool LanguagesAreUnchanged()
        {
            var Unchanged = true;

            var filename = WorkDir + '\\' + "languages.yaml";
            if (!File.Exists(filename))
                File.Create(filename);

            // Если языки программирования изменились
            var mtime = File.GetLastWriteTime(filename);
            if (mtime > LanguagesModificationTime)
            {
                Unchanged = false;
                Logger.Message("Languages change detected");
                Languages = Language.Load(LanguagesDir, filename);
                LanguagesModificationTime = mtime;
            }

            return Unchanged;
        }

        // Проверить решение
        public Result CheckSolution(Problem problem, Language language)
        {
            var result = new Result
            {
                CompilationResult = "CE",
                PreliminaryTestsResults = new Dictionary<string, string>(),
                SubtasksResults = new Dictionary<string, Dictionary<string, string>>()
            };
            foreach (var subtask in problem.Tests)
            {
                foreach (var test in subtask.Value.Tests)
                {
                    language.Execute("", test, problem.MemoryLimit, problem.TimeLimit);
                }
            }
            return result;
        }

        // Конструктор
        public Arbiter(string workDir)
        {
            // Если рабочий каталог отсутствует, то нужно его создать
            WorkDir = workDir;
            if (!Directory.Exists(WorkDir))
            {
                Directory.CreateDirectory(WorkDir);
                Logger.Message("Work directory created: {0}", WorkDir);
            }

            // Если каталог языков программирования отсутствует, то нужно его создать
            LanguagesDir = WorkDir + "\\.languages";
            if (!Directory.Exists(LanguagesDir))
            {
                Directory.CreateDirectory(LanguagesDir);
                Logger.Message("Languages directory created: {0}", LanguagesDir);
            }

            // Если каталог с очередью отсутствует, то нужно его создать
            QueueDir = WorkDir + "\\.queue";
            if (!Directory.Exists(QueueDir))
            {
                Directory.CreateDirectory(QueueDir);
                Logger.Message("Queue directory created: {0}", QueueDir);
            }

            // Если каталог результатов отсутствует, то нужно его создать
            ResultsDir = WorkDir + "\\.results";
            if (!Directory.Exists(ResultsDir))
            {
                Directory.CreateDirectory(ResultsDir);
                Logger.Message("Results directory created: {0}", ResultsDir);
            }

            // Инициализация языков программирования и задач
            Problems = new Dictionary<string, Problem>();
            Languages = new Dictionary<string, Language>();
            LanguagesModificationTime = new DateTime();
        }

        // Стоп-кран
        public static void CancelHandler(object sender, ConsoleCancelEventArgs e)
        {
            if (e.SpecialKey == ConsoleSpecialKey.ControlC)
            {
                UserWantsToStop = true;
                e.Cancel = true;
            }
        }

        // Точка входа
        public static void Main(string[] args)
        {
            var workDir = "";
            if (args.Length >= 1)
                workDir = args[0];

            if (workDir != "")
            {
                Logger.Start();

                // Eсли пользователь нажмет Ctrl+C то дергаем стоп-кран
                Console.CancelKeyPress += new ConsoleCancelEventHandler(CancelHandler);

                Logger.Message("Arbiter started");
                var arbiter = new Arbiter(workDir);
                while (true)
                {
                    try
                    {
                        var result1 = arbiter.LanguagesAreUnchanged();
                        var result2 = arbiter.ProblemsAreUnchanged();
                        var result3 = arbiter.QueueIsEmpty();

                        // Если все было спокойно, то можно секундочку поспать
                        if (result1 && result2 && result3)
                            Thread.Sleep(1000);
                    }
                    catch (Exception e)
                    {
                        Logger.Message("Arbiter stopped due {}", e.Message);
                        break;
                    }
                    if (UserWantsToStop)
                    {
                        Logger.Message("User stopped arbiter");
                        break;
                    }
                }

                Logger.Stop();
            }
            else
            {
                Console.WriteLine("Usage: arbiter.exe workdir");
            }
        }
    }
}