using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using YamlDotNet.Serialization;
using System.IO;

namespace Arbiter.Tests
{
    [TestClass()]
    public class ArbiterTests
    {
        [TestMethod()]
        public void GetDeserializerTest()
        {
            var deserializer = Arbiter.GetDeserializer();
            Assert.IsInstanceOfType(deserializer, typeof(Deserializer));
        }

        //[TestMethod()]
        //public void QueueIsEmptyTest()
        //{
        //    Assert.Fail();
        //}

        //[TestMethod()]
        //public void ProblemsAreUnchangedTest()
        //{
        //    Assert.Fail();
        //}

        //[TestMethod()]
        //public void LanguagesAreUnchangedTest()
        //{
        //    Assert.Fail();
        //}

        //[TestMethod()]
        //public void ArbiterTest()
        //{
        //    Assert.Fail();
        //}

        [TestMethod()]
        public void CheckSolutionTest_CE()
        {
            // Участник отправил решение, которое не компилириуется
            var arbiter = new Arbiter("..\\..\\Fixtures");

            var problem = Problem.Load("..\\..\\Fixtures\\TestProblem1");

            var languages = Language.Load("..\\..\\Fixtures\\.languages", "..\\..\\Fixtures\\languages.yaml");
            var language = languages["msvc"];

            var result = arbiter.CheckSolution(problem, language);

            Assert.IsInstanceOfType(result, typeof(Result));
            Assert.AreEqual("CE", result.CompilationResult);
            Assert.AreEqual(0, result.PreliminaryTestsResults.Count);
            Assert.AreEqual(0, result.SubtasksResults.Count);
            Assert.AreEqual(0, result.Total);
        }

        [TestMethod()]
        public void CheckSolutionTest_Preliminary()
        {
            // Участник отправил решение, которое не компилириуется
            var arbiter = new Arbiter("..\\..\\Fixtures");

            var problem = Problem.Load("..\\..\\Fixtures\\TestProblem2");

            var languages = Language.Load("..\\..\\Fixtures\\.languages", "..\\..\\Fixtures\\languages.yaml");
            var language = languages["msvc"];

            var result = arbiter.CheckSolution(problem, language);

            Assert.IsInstanceOfType(result, typeof(Result));
            Assert.AreEqual("OK", result.CompilationResult);
            Assert.AreEqual(0, result.PreliminaryTestsResults.Count);
            Assert.AreEqual(0, result.SubtasksResults.Count);
            Assert.AreEqual(0, result.Total);
        }

        [TestMethod()]
        public void MainTest()
        {
            var sw = new StringWriter();
            Console.SetOut(sw);

            // Help string
            var args = new string[0];
            Arbiter.Main(args);
            Assert.IsTrue(sw.ToString().Contains("Usage:"));
        }
    }
}