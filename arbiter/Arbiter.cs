
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Arbiter
{
    public class User
    {
        public string Username { get; set; }
        public string LastName { get; set; }
        public string FirstName { get; set; }
        public string SecondName { get; set; }
    }

    public class Problem
    {
        public string Code { get; set; }
        public string CodeName { get; set; }
        public string Name { get; set; }
    }

    public class Result
    {
        public string CompilationResult { get; set; }
        public Dictionary<string, string> PreliminaryResult { get; set; }
        public Dictionary<string, Dictionary<string, string>> ExecutionResult { get; set; }
        public int Total { get; set; }
    }

    public class Submission
    {
        public int Attempt { get; set; }
        public DateTime DateTime { get; set; }
        public User User { get; set; }
        public Problem Problem { get; set; }
        public Result Result { get; set; }
        public string Source { get; set; }
    }

    class Arbiter
    {
        //ThreadStart childref = new ThreadStart(CallToChildThread);
        //Console.WriteLine("In Main: Creating the Child thread");

        //Thread childThread = new Thread(childref);
        //childThread.Start();

        //public static void CallToChildThread()
        //{
            //Console.WriteLine("Child thread starts");
            //for (int counter = 0; counter <= 10; counter++)
            //{
                //Thread.Sleep(500);
                //Console.WriteLine(counter);
            //}
            //Console.WriteLine("Child Thread Completed");
        //}

        static readonly string Queue = "queue";
        static readonly string Results = "results";

        static bool Serialize(string fileName, Submission submission)
        {
            var namingConvention = new UnderscoredNamingConvention();
            var serializer = new SerializerBuilder()
                .WithNamingConvention(namingConvention)
                .EmitDefaults()
                .Build();
            File.WriteAllText(fileName, serializer.Serialize(submission));
            return true;
        }

        static Submission Deserialize (string fileName)
        {
            var fileContent = File.ReadAllText(fileName);
            var namingConvention = new UnderscoredNamingConvention();
            var deserializer = new DeserializerBuilder()
                .WithNamingConvention(namingConvention)
                .Build();
            return deserializer.Deserialize<Submission>(fileContent);
        }

        static string Compile(Submission submission)
        {
            return "OK";
        }

        static Dictionary<string, string> CheckResults(Submission submission)
        {
            return new Dictionary<string, string>() { { "01", "OK" } };
        }

        static bool QueueIsEmpty()
        {
            var queue = Directory.GetFiles(Queue);
            foreach (var fileName in queue)
            {
                if (!fileName.EndsWith(".yaml"))
                    continue;
                try
                {
                    var submission = Deserialize(fileName);
                    submission.Result = new Result();
                    submission.Result.CompilationResult = Compile(submission);
                    if (submission.Result.CompilationResult == "OK")
                    {
                        submission.Result.PreliminaryResult = CheckResults(submission);
                    }
                    Serialize(fileName.Replace(Queue, Results), submission);
                }
                catch (IOException) { }
            }
            return true;
        }

        static void Main(string[] args)
        {
            if (!Directory.Exists(Queue))
                Directory.CreateDirectory(Queue);

            if (!Directory.Exists(Results))
                Directory.CreateDirectory(Results);

            while (QueueIsEmpty())
                Thread.Sleep(1000);

            //var submission = new Submission();
            //submission.Attempt = 1;
            //submission.DateTime = new DateTime();
            //submission.Problem = new Problem { Code = "A", CodeName = "Test", Name = "Тест" };
            //submission.Result = new Result { CompilationResult = "OK", PreliminaryResult = { }, ExecutionResult = { }, Total = 0 };
            //submission.User = new User { Username = "User", LastName = "Петров", FirstName = "Петр", SecondName = "Петрович" };
            //submission.Source = "begin\n\nend.";
            //Serialize(Queue + "\\test.yaml", submission);

            //var submission = Deserialize(Queue + "\\test.yaml");
            //Console.WriteLine("Done");
        }
    }
}
