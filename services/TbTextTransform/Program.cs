using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task<int> Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.WriteLine("Usage: TbTextTransform <inputFileOrDirectory> [outputFileOrDirectory]");
            return 2;
        }

        string input = args[0];
        string output = args.Length > 1 ? args[1] : null;

        try
        {
            var attr = File.GetAttributes(input);
            if ((attr & FileAttributes.Directory) == FileAttributes.Directory)
            {
                string inDir = input;
                string outDir = output ?? Path.Combine(input, "out_upper");
                Directory.CreateDirectory(outDir);
                var files = Directory.GetFiles(inDir, "*.txt");
                foreach (var f in files)
                {
                    string content = await File.ReadAllTextAsync(f);
                    string up = content.ToUpperInvariant();
                    string dest = Path.Combine(outDir, Path.GetFileName(f));
                    await File.WriteAllTextAsync(dest, up);
                    Console.WriteLine($"WROTE:{dest}");
                }
            }
            else
            {
                string content = await File.ReadAllTextAsync(input);
                string up = content.ToUpperInvariant();
                string outFile = output ?? (Path.GetDirectoryName(input) is string dir && dir.Length > 0 ? Path.Combine(dir, Path.GetFileNameWithoutExtension(input) + "_UP" + Path.GetExtension(input)) : (Path.GetFileNameWithoutExtension(input) + "_UP" + Path.GetExtension(input)));
                await File.WriteAllTextAsync(outFile, up);
                Console.WriteLine($"WROTE:{outFile}");
            }

            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("ERROR:" + ex.Message);
            return 1;
        }
    }
}
