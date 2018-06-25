using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Arbiter
{
    public class Logger
    {
        static NLog.Logger LoggerInstance;

        public static void Start()
        {
            var logfile = new NLog.Targets.FileTarget() { FileName = "arbiter.log" };
            var console = new NLog.Targets.ConsoleTarget();
            var config = new NLog.Config.LoggingConfiguration();
            config.AddRuleForAllLevels(logfile);
            config.AddRuleForAllLevels(console);
            NLog.LogManager.Configuration = config;
            LoggerInstance = NLog.LogManager.GetCurrentClassLogger();
        }

        public static void Stop()
        {
            NLog.LogManager.Shutdown();
        }

        public static void Message(string message)
        {
            LoggerInstance.Info(message);
        }

        public static void Message(string message, string arg)
        {
            LoggerInstance.Info(message, arg);
        }
    }


    // Подзадача
    public class Subtask
    {
        public string Scoring { get; set; }  // Начисление баллов: partial / entire
        public string Information { get; set; }  // Информация для пользователей: full / brief
        public int Score { get; set; }  // Количество баллов за подзадачу

        // Проверить решение
        public int CheckSolution()
        {
            // TODO: Проверить решение на тестах подзадачи
            return 0;
        }
    }


    // Задача
    public class Problem
    {
        public string Name { get; set; }  // Название
        public int TimeLimit { get; set; } // Лимит времени в миллисекундах
        public int MemoryLimit { get; set; } // Лимит памяти в мегабайтах
        public Dictionary<string, Subtask> Subtasks { get; set; }  // Подзадачи
        public List<string> PreliminaryTests { get; set; }  // Предварительные тестые
        public DateTime ModificationTime;  // Дата и время изменения

        // Проверить решение
        public static Problem Load(string filename)
        {
            var content = File.ReadAllText(filename);
            Problem result = null;
            try
            {
                result = Arbiter.GetDeserializer().Deserialize<Problem>(content);
            }
            catch (YamlDotNet.Core.YamlException e)
            {
                Logger.Message(filename + ":" + e.Message + "(" + e.InnerException.Message + ")");
            }
            return result;
        }

        // Проверить задачу
        public bool Check()
        {
            var result = true;

            // TODO: Проверить, что сумма баллов равна 100

            // TODO: Проверить, что чекер работает с предварительными тестами

            // TODO: Проверить, что чекер работает с основными тестами

            return result;
        }

        // Проверить решение
        public Result CheckSolution()
        {
            // TODO: Скомпилировать решение, проверить решение на предварительных и основных тестах
            return null;
        }
    }

    // Язык программирования
    public class Language
    {
        public string Name { get; set; }  // Название
        public List<string> Compilation { get; set; }  // Шаги компиляции
        public string Execution { get; set; }  // Выполнение

        // Компиляция
        public string Compile(Language language, string source)
        {
            var result = "OK";
            try
            {
                // TODO: Скомпилировать решение с помощью bat-файла
            }
            catch
            {
                result = "CE";
            }
            return result;
        }

        // Компиляция
        public string Execute()
        {
            var result = "OK";
            try
            {
                // TODO: Запустить решение на тесте
            }
            catch
            {
                result = "CE";
            }
            return result;
        }

        // Создание bat-файла для компиляции решения
        public void CreateBatchFile(string languagesDir, string code)
        {
            var filename = languagesDir + '\\' + code + ".bat";
            var file = File.CreateText(filename);
            foreach (var str in Compilation)
                file.WriteLine(str);
            file.Close();
        }

        // Проверка языка программирования
        public bool Check()
        {
            var result = true;

            // TODO: Проверить, что для основных языков компиляция происходит без ошибок

            // TODO: Проверить, что исполняемый файл работает

            return result;
        }

        // Загрузка списка языков программирования из YAML-файла
        public static Dictionary<string, Language> Load(string languagesDir, string filename)
        {
            Dictionary<string, Language> result = null;

            // Удаляем старые bat-файлы
            var batchFiles = Directory.GetFiles(languagesDir, "*.bat");
            foreach (var batchFile in batchFiles)
                File.Delete(batchFile);

            // Читаем файл
            try
            {
                var content = File.ReadAllText(filename);
                result = Arbiter.GetDeserializer().Deserialize<Dictionary<string, Language>>(content);
            }
            catch (YamlDotNet.Core.YamlException e)
            {
                Logger.Message(filename + ": " + e.Message + " (" + e.InnerException.Message + ")");
            }

            // Если чтение не удалось тогда создаем пустой словарь
            if (result == null)
                result = new Dictionary<string, Language>();

            // Проверяем результат
            foreach (var entry in result)
            {
                var code = entry.Key;
                var language = entry.Value;
                if (language.Check())
                {
                    // Если все нормально, то создаем bat-файл
                    language.CreateBatchFile(languagesDir, code);
                    Logger.Message("Language {} successfully checked. Changes are committed.", code);
                }
                else
                {
                    // Если проверка не удалась, удаляем язык программирования
                    result.Remove(code);
                    Logger.Message("Languages {} check failed. Language was removed.", code);
                }
            }

            return result;
        }
    }


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

        public Dictionary<string, Language> Languages;
        public Dictionary<string, Problem> Problems;
        public DateTime LanguagesModificationTime;

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
        bool ProblemsAreUnchanged()
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
                if (dirname.ToLower() == LanguagesDir.ToLower()
                    || dirname.ToLower() == QueueDir.ToLower()
                    || dirname.ToLower() == ResultsDir.ToLower())
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
                var problem = Problem.Load(filename);
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
        static void CancelHandler(object sender, ConsoleCancelEventArgs e)
        {
            if (e.SpecialKey == ConsoleSpecialKey.ControlC)
            {
                UserWantsToStop = true;
                e.Cancel = true;
            }
        }

        // Точка входа
        static void Main(string[] args)
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