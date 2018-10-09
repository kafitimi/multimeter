using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics;

namespace Arbiter
{
    public class Subtask
    {
        public List<string> Tests;  // Имена тестов
        public int Score { get; set; }  // Количество баллов за подзадачу
        public string Scoring { get; set; }  // Начисление баллов: partial / entire
        public string Information { get; set; }  // Информация для пользователей: full / brief
    }

    // Задача
    public class Problem
    {
        public string Name { get; set; }  // Название
        public int TimeLimit { get; set; }  // Лимит времени в миллисекундах
        public int MemoryLimit { get; set; }  // Лимит памяти в мегабайтах
        public Dictionary<string, Subtask> Tests { get; set; }  // Настройки подзадач

        public string Code;  // Код задачи
        public string ProblemFile;  // Файл описания задачи
        public string CheckerFile;  // Файл чекера
        public string SubtasksDir;  // Каталог для подзадач
        public string SolutionsDir;  // Каталог для решений
        public string PreliminaryTestsDir;  // Каталог предварительных тестов
        public DateTime ModificationTime;  // Дата и время изменения
        public List<string> PreliminaryTests;  // Файлы предварительных тестов
        
        // Загрузить задачу из YAML-файла
        public static Problem Load(string problemDir)
        {
            Problem problem = null;
            var problemFile = problemDir + '\\' + "problem.yaml";
            try
            {
                var content = File.ReadAllText(problemFile);
                problem = Arbiter.GetDeserializer().Deserialize<Problem>(content);
                problem.Code = problemDir.Substring(problemDir.LastIndexOf('\\') + 1);
                problem.ProblemFile = problemFile;
                problem.CheckerFile = problemDir + '\\' + "check.exe";
                problem.SubtasksDir = problemDir + '\\' + "tests";
                problem.SolutionsDir = problemDir + '\\' + "solutions";
                problem.PreliminaryTestsDir = problemDir + '\\' + "preliminary";
                problem.ModificationTime = File.GetLastWriteTime(problemFile);
                problem.PreliminaryTests = new List<string>();
                var tests = Directory.GetFiles(problem.PreliminaryTestsDir);
                foreach (var test in tests)
                {
                    var answerFile = test + ".a";
                    if (File.Exists(answerFile))
                        problem.PreliminaryTests.Add(test);
                }
                foreach (var subtask in problem.Tests)
                {
                    var testsDir = problem.SubtasksDir + '\\' + subtask.Key;
                    subtask.Value.Tests = new List<string>();
                    tests = Directory.GetFiles(testsDir);
                    foreach (var test in tests)
                    {
                        var answerFile = test + ".a";
                        if (File.Exists(answerFile))
                            subtask.Value.Tests.Add(test);
                    }
                }
            }
            catch (YamlDotNet.Core.YamlException e)
            {
                Logger.Message(problemFile + ":" + e.Message + "(" + e.InnerException.Message + ")");
            }
            return problem;
        }

        // Проверить задачу
        public bool Check()
        {
            var result = true;

            // Проверка, что сумма баллов равна 100
            var sum = 0;
            foreach (var subtask in Tests)
            {
                var st = subtask.Value;

                if (st.Scoring.ToLower() == "entire")
                    sum += st.Score;

                if (st.Scoring.ToLower() == "full")
                    sum += st.Score * st.Tests.Capacity;
            }
            if (sum != 100)
            {
                Logger.Message("Problem {}: Total sum of points != 100.", Code);
                result = false;
            }

            // Проверка на наличие чекера
            if (result && !File.Exists(CheckerFile))
            {
                Logger.Message("Problem {}: Checker does not exist.", Code);
                result = false;
            }

            // Проверка, что чекер работает с предварительными тестами
            if (result)
            {
                foreach (var test in PreliminaryTests)
                {
                    var psi = new ProcessStartInfo
                    {
                        Arguments = test + " " + test + ".a",
                        FileName = CheckerFile,
                        WorkingDirectory = PreliminaryTestsDir
                    };
                    try
                    {
                        Process.Start(psi);
                    }
                    catch
                    {
                        Logger.Message("Problem {}: Checker does not work with preliminary test {}.", Code, test);
                        result = false;
                    }
                }
            }

            // Проверка, что чекер работает с основными тестами
            if (result)
            {
                foreach (var subtask in Tests)
                {
                    var testsDir = SubtasksDir + '\\' + subtask.Key;
                    var tests = Directory.GetFiles(testsDir);
                    foreach (var test in tests)
                    {
                        var testFilename = test.Substring(test.LastIndexOf('\\') + 1);
                        var psi = new ProcessStartInfo
                        {
                            Arguments = test + " " + test + ".a",
                            FileName = CheckerFile,
                            WorkingDirectory = testsDir
                        };
                        try
                        {
                            Process.Start(psi);
                        }
                        catch
                        {
                            Logger.Message("Problem {}: Checker does not work with primary test {}.", Code, test);
                            result = false;
                        }
                    }
                }
            }

            return result;
        }
    }
}