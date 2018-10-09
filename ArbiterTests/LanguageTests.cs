using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.IO;

/* Обязаннасти класса Language:
 * - считать и распарсить список описаний языков программирования
 * - 
 */

namespace Arbiter.Tests
{
    [TestClass()]
    public class LanguageTests
    {
        [TestMethod()]
        public void CompileTest()
        {
            var language = new Language
            {
                Name = "Compiler",
                Execution = "%1.exe",
                Compilation = "call \"C:\\Program Files(x86)\\Microsoft Visual Studio\\2017\\Community\\Common7\\Tools\\VsDevCmd.bat\"\ncl %1.cpp\n"
            };
            var directory = "..\\..\\Fixtures";
            language.CreateBatchFile(directory, "test");
            var filename = "source.cpp";
            File.WriteAllText(directory + '\\' + filename, "int main() { return 0; }");
            Assert.AreEqual("OK", language.Compile(directory, filename));
            File.WriteAllText(directory + '\\' + filename, "ind main() { return 0; }");
            Assert.AreEqual("CE", language.Compile(directory, filename));
        }

        //[TestMethod()]
        //public void ExecuteTest()
        //{
        //    Assert.Fail();
        //}

        [TestMethod()]
        public void CreateBatchFileTest()
        {
            var directory = "..\\..\\Fixtures";
            var filename = "test";
            var full_path = directory + "\\" + filename + ".bat";
            File.Delete(full_path);
            var language = new Language
            {
                Name = "compiler",
                Execution = "",
                Compilation = "1\n2\n3"
            };
            language.CreateBatchFile(directory, filename);
            var content = File.ReadAllText(full_path);
            Assert.AreEqual(language.Compilation, content);
        }

        //[TestMethod()]
        //public void CheckTest()
        //{
        //    Assert.Fail();
        //}

        [TestMethod()]
        public void LoadTest()
        {
            var directory = "..\\..\\Fixtures\\.languages";
            var filename = "..\\..\\Fixtures\\languages.yaml";
            var languages = Language.Load(directory, filename);
            Assert.IsInstanceOfType(languages, typeof(Dictionary<string, Language>));
            Assert.AreEqual(1, languages.Count);
            var language = languages["msvc"];
            Assert.AreEqual("call \"C:\\Program Files(x86)\\Microsoft Visual Studio\\2017\\Community\\Common7\\Tools\\VsDevCmd.bat\"\ncl %1.cpp\n", language.Compilation);
            Assert.AreEqual("MS Visual C++", language.Name);
            Assert.AreEqual("%1.exe", language.Execution);
        }
    }
}