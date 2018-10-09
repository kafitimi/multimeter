//using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.IO;

namespace Arbiter.Tests
{
    //[TestClass()]
    public class ArbiterTests
    {
        //[TestMethod()]
        //public void SerializeTest()
        //{
        //    Logger.Start();

        //    Submission submission = new Submission()
        //    {
        //        Attempt = 1,
        //        Language = "Gcc",
        //        Problem = "A",
        //        Result = new Result()
        //        {
        //            CompilationResult = "OK",
        //            PreliminaryTestsResults = new Dictionary<string, string>
        //            {
        //                { "01", "OK" },
        //                { "02", "OK" },
        //            },
        //        },
        //        Source = "begin\nend.",
        //        SubmissionTime = new DateTime(2018, 1, 1, 0, 0, 0),
        //        User = "Last First",
        //    };

        //    var filename = "test.yaml";
        //    Assert.IsTrue(Arbiter.Serialize(filename, submission));
        //    var content = File.ReadAllText(filename);
        //    Assert.IsTrue(content.Contains("Last First"));
        //    Assert.IsTrue(content.Contains("Gcc"));
        //    Assert.IsTrue(content.Contains("01"));
        //    Assert.IsTrue(content.Contains("02"));
        //    Assert.IsTrue(content.Contains("OK"));
        //    Assert.IsTrue(content.Contains("begin"));
        //    Assert.IsTrue(content.Contains("end"));
        //    Assert.IsTrue(content.Contains("2018-01-01T00:00:00"));

        //    Logger.Stop();
        //}

        //[TestMethod()]
        //public void DeserializeSubmissionTest()
        //{
        //    Logger.Start();

        //    var filename = "test.yaml";
        //    Submission submission = Arbiter.DeserializeSubmission(filename);
        //    Assert.AreEqual(1, submission.Attempt);
        //    Assert.AreEqual("Gcc", submission.Language);
        //    Assert.AreEqual("A", submission.Problem);
        //    Assert.AreEqual("OK", submission.Result.CompilationResult);
        //    Assert.AreEqual("OK", submission.Result.PreliminaryTestsResults["01"]);
        //    Assert.AreEqual("OK", submission.Result.PreliminaryTestsResults["02"]);
        //    Assert.AreEqual("begin\nend.", submission.Source);
        //    Assert.AreEqual(new DateTime(2018, 1, 1, 0, 0, 0), submission.SubmissionTime);
        //    Assert.AreEqual("Last First", submission.User);

        //    Logger.Stop();
        //}
    }
}