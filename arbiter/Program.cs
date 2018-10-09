// Для совместимости с Windows XP целевой платформой является 32-битная версия .Net Framework 4.0
// Нужно установить пакет DllExport с помощью NuGet

using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

// Информация о процессе
public struct PROCESS_INFORMATION
{
    public IntPtr hProcess;     // HANDLE
    public IntPtr hThread;      // HANDLE
    public uint dwProcessId;    // DWORD
    public uint dwThreadId;     // DWORD
}

// Информация о запуске процесса
public struct STARTUPINFO
{
    public uint cb;                 // DWORD
    public string lpReserved;       // LPTSTR
    public string lpDesktop;        // LPTSTR
    public string lpTitle;          // LPTSTR
    public uint dwX;                // DWORD
    public uint dwY;                // DWORD
    public uint dwXSize;            // DWORD
    public uint dwYSize;            // DWORD
    public uint dwXCountChars;      // DWORD
    public uint dwYCountChars;      // DWORD
    public uint dwFillAttribute;    // DWORD
    public uint dwFlags;            // DWORD
    public ushort wShowWindow;      // WORD
    public ushort cbReserved2;      // WORD
    public IntPtr lpReserved2;      // LPBYTE
    public IntPtr hStdInput;        // HANDLE
    public IntPtr hStdOutput;       // HANDLE
    public IntPtr hStdError;        // HANDLE
}

// Атрибуты безопасности
public struct SECURITY_ATTRIBUTES
{
    public uint nLength;                // DWORD
    public IntPtr lpSecurityDescriptor; // LPVOID
    public bool bInheritHandle;         // BOOL
}

// Метрики памяти процесса
public struct PROCESS_MEMORY_COUNTERS
{
    public uint cb;                             // DWORD
    public uint PageFaultCount;                 // DWORD
    public uint PeakWorkingSetSize;             // SIZE_T
    public uint WorkingSetSize;                 // SIZE_T
    public uint QuotaPeakPagedPoolUsage;        // SIZE_T
    public uint QuotaPagedPoolUsage;            // SIZE_T
    public uint QuotaPeakNonPagedPoolUsage;     // SIZE_T
    public uint QuotaNonPagedPoolUsage;         // SIZE_T
    public uint PagefileUsage;                  // SIZE_T
    public uint PeakPagefileUsage;              // SIZE_T
}

// Момент времени
public struct SYSTEMTIME
{
    public ushort wYear;            // WORD
    public ushort wMonth;           // WORD
    public ushort wDayOfWeek;       // WORD
    public ushort wDay;             // WORD
    public ushort wHour;            // WORD
    public ushort wMinute;          // WORD
    public ushort wSecond;          // WORD
    public ushort wMilliseconds;    // WORD
}

// Режимы защиты отображения файла
enum FileMapProtection : uint
{
    PageReadonly = 0x02,
    PageReadWrite = 0x04,
    PageWriteCopy = 0x08,
    PageExecuteRead = 0x20,
    PageExecuteReadWrite = 0x40,
    SectionCommit = 0x8000000,
    SectionImage = 0x1000000,
    SectionNoCache = 0x10000000,
    SectionReserve = 0x4000000,
}

namespace invoker
{
    [ComVisible(true)]
    public class Invoker
    {
        // Константы
        public const uint GENERIC_READ = 0x80000000;
        public const uint FILE_SHARE_READ = 0x00000001;
        public const uint GENERIC_WRITE = 0x40000000;
        public const uint FILE_SHARE_WRITE = 0x00000002;
        public const uint CREATE_ALWAYS = 1;
        public const uint OPEN_ALWAYS = 4;
        public const uint FILE_ATTRIBUTE_NORMAL = 0x00000080;
        public const uint STARTF_USESTDHANDLES = 0x00000100;
        public const ulong WAIT_OK = 0L;
        public const ulong WAIT_TIMEOUT = 258L;

        // Запуск процесса
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool CreateProcess(
            string lpApplicationName,                     // LPCSTR
            string lpCommandLine,                         // LPSTR
            IntPtr lpProcessAttributes,                   // LPSECURITY_ATTRIBUTES
            IntPtr lpThreadAttributes,                    // LPSECURITY_ATTRIBUTES
            bool bInheritHandles,                         // BOOL
            uint dwCreationFlags,                         // DWORD
            IntPtr lpEnvironment,                         // LPVOID
            string lpCurrentDirectory,                    // LPCSTR
            ref STARTUPINFO lpStartupInfo,                // LPSTARTUPINFO
            ref PROCESS_INFORMATION lpProcessInformation  // LPPROCESS_INFORMATION
        );

        // Открытие файла
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern IntPtr CreateFile(
            string lpFileName,                              // LPCSTR lpFileName
            uint dwDesiredAccess,                           // DWORD dwDesiredAccess
            uint dwSharedMode,                              // DWORD dwSharedMode
            ref SECURITY_ATTRIBUTES lpSecurityAttributes,   // LPSECURITY_ATTRIBUTES lpSecurityAttributes
            uint dwCreationDisposition,                     // DWORD dwCreationDisposition
            uint dwFladsAndAttributes,                      // DWORD dwFladsAndAttributes
            IntPtr hTemplateFile                            // HANDLE hTemplateFile
        );

        // Открытие отображения файла в память
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern IntPtr CreateFileMapping(
            IntPtr hFile,                                   // LPCSTR lpFileName
            IntPtr lpFileMappingAttributes,                 // DWORD dwDesiredAccess
            FileMapProtection flProtect,                    // DWORD dwSharedMode
            uint dwMaximumSizeHigh,                         // LPSECURITY_ATTRIBUTES lpSecurityAttributes
            uint dwMaximumSizeLow,                          // DWORD dwCreationDisposition
            string lpName,                                  // DWORD dwFladsAndAttributes
            IntPtr hTemplateFile                            // HANDLE hTemplateFile
        );

        // Завершение процесса
        [DllImport("kernel32.dll")]
        static extern bool TerminateProcess(
            IntPtr hProcess,                                // HANDLE
            uint uExitCode                                  // UINT
        );

        // Ожидание завершения процесса
        [DllImport("kernel32.dll")]
        static extern uint WaitForSingleObject(
            IntPtr hHandle,                                 // HANDLE
            uint dwMilliseconds                             // DWORD
        );

        // Завершить работу с дескриптором
        [DllImport("kernel32.dll")]
        static extern void CloseHandle(
            IntPtr hHandle                                  // HANDLE
        );

        // Получить момент времени
        [DllImport("kernel32.dll")]
        static extern void GetSystemTime(
            ref SYSTEMTIME lpSystemTime                     // LPSYSTEMTIME
        );

        // Получить информацию о памяти процесса
        [DllImport("psapi.dll", SetLastError = true)]
        static extern bool GetProcessMemoryInfo(
            IntPtr hProcess,                                // HANDLE
            ref PROCESS_MEMORY_COUNTERS counters,           // PPROCESS_MEMORY_COUNTERS
            uint size                                       // DWORD
        );

        // Абсолютное значение числа
        public static uint Abs(int number)
        {
            return (uint)((number >= 0) ? number : -number);
        }

        // Стартовая информация
        public static STARTUPINFO si;

        // Информация о процессе
        public static PROCESS_INFORMATION pi;

        // Режим наследования файловых дескрипторов
        public static bool inheritance;

        // Запуск Windows приложения
        public static bool Windows_generic(
            string executable,
            ref uint memory,
            ref uint time
        )
        {
            // Информация о процессе
            pi = new PROCESS_INFORMATION();

            // Момент запуска дочернего процесса
            SYSTEMTIME startTime = new SYSTEMTIME();
            GetSystemTime(ref startTime);

            // Запускаем дочерний процесс
            bool result = CreateProcess(
                executable,
                null,
                IntPtr.Zero,
                IntPtr.Zero,
                inheritance,
                0,
                IntPtr.Zero,
                null,
                ref si,
                ref pi
            );
            if (!result)
                return false;

            // Ожидание завершения процесса
            uint res_code = WaitForSingleObject(pi.hProcess, (uint)time);
            if (res_code == WAIT_TIMEOUT)
            {
                TerminateProcess(pi.hProcess, (uint)0);
            }
            else if (res_code != WAIT_OK)
            {
                return false;
            }

            // Момент завершения дочернего процесса
            SYSTEMTIME stopTime = new SYSTEMTIME();
            GetSystemTime(ref stopTime);

            // Время работы в миллисекундах
            time =
                Abs(stopTime.wHour - startTime.wHour) * 60 * 60 * 1000 +
                Abs(stopTime.wMinute - startTime.wMinute) * 60 * 1000 +
                Abs(stopTime.wSecond - startTime.wSecond) * 1000 +
                Abs(stopTime.wMilliseconds - startTime.wMilliseconds);

            // Получим данные об использовании памяти
            PROCESS_MEMORY_COUNTERS pmc = new PROCESS_MEMORY_COUNTERS();
            pmc.cb = (uint)Marshal.SizeOf(typeof(PROCESS_MEMORY_COUNTERS));
            result = GetProcessMemoryInfo(pi.hProcess, ref pmc, pmc.cb);

            // Память использованная процессом
            memory = pmc.PeakPagefileUsage;

            // Завершаем работу с дескрипторами
            CloseHandle(pi.hProcess);

            return true;
        }

        // Запуск Windows приложения с файловым входным файлом
        // [DllExport(CallingConvention = CallingConvention.Cdecl)]
        public static bool Windows_file(
            string executable,
            ref uint memory,
            ref uint time
        )
        {
            // Режим наследования файловых дескрипторов
            inheritance = false;

            // Стартовая информация
            si = new STARTUPINFO
            {
                cb = (uint)Marshal.SizeOf(typeof(STARTUPINFO))
            };

            return Windows_generic(executable, ref memory, ref time);
        }

        // [DllExport(CallingConvention = CallingConvention.Cdecl)]
        public static bool console(
            string executable,
            string input,
            string output,
            ref uint memory,
            ref uint time
        )
        {
            // Режим наследования файловых дескрипторов
            inheritance = true;

            // Разрешаем дочернему процессу использовать входной и выходной файлы
            SECURITY_ATTRIBUTES securityAttributes = new SECURITY_ATTRIBUTES
            {
                nLength = (uint)Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES)),
                lpSecurityDescriptor = IntPtr.Zero,
                bInheritHandle = inheritance
            };

            // Входной файл
            IntPtr hStdInput = CreateFile(
                input,                  // LPCSTR lpFileName
                GENERIC_READ,           // DWORD dwDesiredAccess
                FILE_SHARE_READ,        // DWORD dwSharedMode
                ref securityAttributes, // LPSECURITY_ATTRIBUTES lpSecurityAttributes
                OPEN_ALWAYS,            // DWORD dwCreationDisposition
                FILE_ATTRIBUTE_NORMAL,  // DWORD dwFladsAndAttributes
                IntPtr.Zero             // HANDLE hTemplateFile
            );

            // Выходной файл
            IntPtr hStdOutput = CreateFile(
                output,                 // LPCSTR lpFileName
                GENERIC_WRITE,          // DWORD dwDesiredAccess
                FILE_SHARE_WRITE,       // DWORD dwSharedMode
                ref securityAttributes, // LPSECURITY_ATTRIBUTES lpSecurityAttributes
                CREATE_ALWAYS,          // DWORD dwCreationDisposition
                FILE_ATTRIBUTE_NORMAL,  // DWORD dwFladsAndAttributes
                IntPtr.Zero             // HANDLE hTemplateFile
            );

            // Стартовая информация
            si = new STARTUPINFO
            {
                cb = (uint)Marshal.SizeOf(typeof(STARTUPINFO)),
                dwFlags = STARTF_USESTDHANDLES,
                hStdInput = hStdInput,
                hStdOutput = hStdOutput,
                hStdError = IntPtr.Zero
            };

            bool result = Windows_generic(executable, ref memory, ref time);

            CloseHandle(hStdInput);
            CloseHandle(hStdOutput);

            return result;
        }

        //        [DllExport(CallingConvention = CallingConvention.Cdecl)]
        //        public static bool Clr_file(
        //            string executable,
        //            ref uint memory,
        //            ref uint time
        //        )
        //        {
        //            // Создание дочернего процесса
        //            Process p = new Process();
        //            p.StartInfo.FileName = executable;
        //            p.StartInfo.CreateNoWindow = true;

        //            // Момент запуска дочернего процесса
        //            DateTime startTime = DateTime.Now;

        //            // Запуск дочернего процесса
        //            p.Start();

        ////            Console.WriteLine(p.PeakVirtualMemorySize64.ToString()); // !!!!!!! это дибах, детка !!!!!!!!!

        //            // Ожидание завершения дочернего процесса
        //            p.WaitForExit((int)time);

        //            // Если процесс ещё не завершен - завершаем его принудительно
        //            if (!p.HasExited)
        //            {
        //                Console.WriteLine("Oops");
        //                p.Kill();
        //            }

        //            // Момент завершения дочернего процесса
        //            DateTime stopTime = DateTime.Now;

        //            // Время работы в миллисекундах
        //            time =
        //                Abs(stopTime.Hour - startTime.Hour) * 60 * 60 * 1000 +
        //                Abs(stopTime.Minute - startTime.Minute) * 60 * 1000 +
        //                Abs(stopTime.Second - startTime.Second) * 1000 +
        //                Abs(stopTime.Millisecond - startTime.Millisecond);

        //            Console.WriteLine("Stage7 " + time.ToString());

        //            Console.WriteLine(p.PeakVirtualMemorySize64.ToString());

        //            // Память использованная процессом
        //            memory = (uint)p.PeakVirtualMemorySize64;

        //            Console.WriteLine("Stage8 " + memory.ToString());

        //            return true;
        //        }

        //[DllExport(CallingConvention = CallingConvention.Cdecl)]
        //public static bool Clr_console(
        //    string executable,
        //    string input,
        //    string output,
        //    ref uint memory,
        //    ref uint time
        //)
        //{
        //    return true;
        //}
    }
}
