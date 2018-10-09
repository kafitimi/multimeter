namespace Arbiter
{
    class Logger
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

        public static void Message(string message, params object[] args)
        {
            if (LoggerInstance != null)
                LoggerInstance.Info(message, args);
        }
    }
}