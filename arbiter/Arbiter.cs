using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Arbiter
{
    // Подзадача
    public class Subtask
    {
        public string Scoring { get; set; }  // Начисление баллов: partial / entire
        public string Information { get; set; }  // Информация для пользователей: full / brief
        public int Score { get; set; }  // Количество баллов за подзадачу
    }

    // Задача
    public class Problem
    {
        public string Name { get; set; }  // Название
        public Dictionary<string, Subtask> Subtasks { get; set; }  // Подзадачи
        public DateTime ModificationTime { get; set; }  // Дата и время изменения
    }

    // Язык программирования
    public class Language
    {
        public string Name { get; set; }  // Название
        public List<string> Compilation { get; set; }  // Шаги компиляции
        public string Execution { get; set; }  // Выполнение
        public DateTime ModificationTime { get; set; }  // Дата и время изменения
    }

    // Результат проверки
    public class Result
    {
        public string CompilationResult { get; set; }  // Результат компиляции
        public Dictionary<string, string> PreliminaryTestsResults { get; set; }  // Результаты проверки на предварительных тестах
        public Dictionary<string, Dictionary<string, string>> SubtasksResults { get; set; }  // Результаты проверки на подзадачах
        public int Total { get; set; }  // Общий балл
    }

    // Отправка
    public class Submission
    {
        public int Attempt { get; set; }  // Номер попытки
        public DateTime SubmissionTime { get; set; }  // Дата и время отправки
        public string User { get; set; }  // Пользователь
        public string Problem { get; set; }  // Код задачи
        public string Language { get; set; }  // Код языка программирования
        public Result Result { get; set; }  // Результат проверки
        public string Source { get; set; }  // Исходный код решения
    }

    // Арбитр
    class Arbiter
    {
        readonly string SettingsFolder = "settings";
        readonly string QueueFolder = "queue";
        readonly string ResultsFolder = "results";
        Dictionary<string, Language> Languages;
        Dictionary<string, Problem> Problems;

        // Запись YAML-файла
        bool Serialize(string fileName, Object submission)
        {
            var serializer = new SerializerBuilder()
                .WithNamingConvention(new UnderscoredNamingConvention())
                .EmitDefaults()
                .Build();
            File.WriteAllText(fileName, serializer.Serialize(submission));
            return true;
        }

        // Чтение и парсинг YAML-файла
        Submission DeserializeSubmission(string fileName)
        {
            var fileContent = File.ReadAllText(fileName);
            var deserializer = new DeserializerBuilder()
                .WithNamingConvention(new UnderscoredNamingConvention())
                .Build();
            return deserializer.Deserialize<Submission>(fileContent);
        }

        // Компиляция
        string Compilation(Language language, string source)
        {
            var result = "OK";
            try
            {
                // Нужно выполнить шаги компиляции
            }
            catch
            {
                result = "CE";
            }
            return result;
        }

        // Проверка на тестов подзадачи
        Dictionary<string, string> SubtaskCheck(Language language, Dictionary<string, Subtask> subtasks)
        {
            var result = new Dictionary<string, string>();
            foreach (KeyValuePair<string, Subtask> entry in subtasks)
            {
                result[entry.Key] = "OK";
                try
                {
                    // Проверить тест
                }
                catch
                {
                    result[entry.Key] = "RE";
                }
            }
            return result;
        }

        // Проверка на предварительных тестах
        Dictionary<string, string> PreliminaryTestsCheck(Language language, Problem problem, Submission submission)
        {
            var result = new Dictionary<string, string>();
            var preliminaryFolder = "";
            var queue = Directory.GetFiles(preliminaryFolder);
            foreach (KeyValuePair<string, Subtask> entry in subtasks)
            {
                try
                {
                    submission.Result.PreliminaryTestsResults = new Dictionary<string, string>(){ { "01", "OK" } };
                }
                catch
                {
                    result[entry.Key] = "RE";
                }
            }
            return result;
        }

        // Если настройки изменились, надо их проверить
        bool SettingsAreUnchanged()
        {
            var Unchanged = true;

            return Unchanged;
        }

        // Обход файлов в очереди
        bool QueueIsEmpty()
        {
            var Empty = true;  // Нужно, чтобы определить можно ли поспать или нет
            var queue = Directory.GetFiles(QueueFolder);
            foreach (var fileName in queue)  // fileName включает в себя имя каталога
            {
                // Пропускаем ненужные файлы
                if (!fileName.EndsWith(".yaml"))
                    continue;

                Empty = false;  // Блин, не получиться поспать

                // Переместим файл, чтобы в следующий раз не обработать его повторно
                var newFileName = fileName.Replace(QueueFolder, ResultsFolder);
                // !!! Загуглить как перемещать файлы

                var submission = DeserializeSubmission(newFileName);
                submission.Result = new Result();
                var language = Languages[submission.Language];
                if (Compilation(language, submission.Source) == "OK")
                {
                    var problem = Problems[submission.Problem];
                    if (PreliminaryTestsCheck(language, problem, submission) == "OK")
                    {
                        var total = 0;
                        foreach (KeyValuePair<string, Subtask> entry in problem.Subtasks)
                        {
                            SubtaskCheck(submission, language, entry.Value);
                        }
                        submission.Result.Total = total;
                    }
                }

                Serialize(newFileName, submission);
            }
            return Empty;
        }

        // Конструктор
        Arbiter()
        {
            // Если каталог с настройками отсутствует, то нужно его создать
            if (!Directory.Exists(SettingsFolder))
                Directory.CreateDirectory(SettingsFolder);

            // Если каталог с очередью отсутствует, то нужно его создать
            if (!Directory.Exists(QueueFolder))
                Directory.CreateDirectory(QueueFolder);

            // Если каталог результатов отсутствует, то нужно его создать
            if (!Directory.Exists(ResultsFolder))
                Directory.CreateDirectory(ResultsFolder);
        }

        // Точка входа
        static void Main(string[] args)
        {
            var arbiter = new Arbiter();
            while (true)
            {
                // Если работы нет, то можно секундочку поспать
                if (arbiter.SettingsAreUnchanged() && arbiter.QueueIsEmpty())
                    Thread.Sleep(1000);
            }
        }
    }
}
