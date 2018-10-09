using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace Arbiter
{
    public class Language
    {
        public string Name { get; set; }  // Название
        public string Execution { get; set; }  // Выполнение
        public string Compilation { get; set; }  // Шаги компиляции

        public string CompilationBatch;  // Пакетный файл

        // Компиляция
        public string Compile(string workingDir, string filename)
        {
            var verdict = "OK";
            var process = new Process();
            process.StartInfo.Arguments = filename;
            process.StartInfo.FileName = CompilationBatch;
            process.StartInfo.WorkingDirectory = workingDir;
            process.Start();
            if (process.ExitCode != 0)
                verdict = "CE";
            return verdict;
        }

        // Выполнение
        public string Execute(string workingDir, string filename, int MemoryLimit, int TimeLimit)
        {
            var verdict = "OK";
            //var process = new Process();
            //try
            //{
            //    process.StartInfo.FileName = filename;
            //    process.StartInfo.RedirectStandardInput = true;
            //    process.StartInfo.RedirectStandardOutput = true;
            //    process.StartInfo.WorkingDirectory = workingDir;
            //    process.WaitForExit(TimeLimit);
            //    var before = DateTime.Now;
            //    process.Start();
            //    var after = DateTime.Now;

            //    if (process.ExitCode != 0)
            //        verdict = "RE";
            //    if (process.PeakVirtualMemorySize64 > MemoryLimit)
            //        verdict = "ML";
            //    if ((after - before).Milliseconds > TimeLimit)
            //        verdict = "TL";
            //    // Check for wrong answer
            //}
            //catch
            //{
            //    verdict = "RE";
            //}
            return verdict;
        }

        // Создание bat-файла для компиляции решения
        public void CreateBatchFile(string languagesDir, string code)
        {
            CompilationBatch = languagesDir + '\\' + code + ".bat";
            File.WriteAllText(CompilationBatch, Compilation);
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
                if (e.InnerException == null)
                    Logger.Message("{}: {} ({})", filename, e.Message);
                else
                    Logger.Message("{}: {} ({})", filename, e.Message, e.InnerException.Message);
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
}