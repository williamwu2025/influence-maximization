using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;

namespace InfluenceMaximization
{
    class MainClass
    {
        public static string filepath = "/home/sjtuiiot/wcy/im/Wiki-Vote";
        //public static string filepath = "D:/iiot/csharp/im/Wiki-Vote";
        public static void Main(string[] args)
        {
            Graph graph = new Graph(filepath+".csv");
            
            CoordinateDescentAlgCommonHyperGraphOneAlpha(graph);
         }
        public static void CoordinateDescentAlgCommonHyperGraphOneAlpha(Graph graph)
        {
            StreamReader initial = new StreamReader(filepath+"_ini100.txt");
            StreamReader nodetype = new StreamReader(filepath + "_typeo.txt");
            StreamReader threshold = new StreamReader(filepath + "_tu.txt");
            List<double> thresh = new List<double>();
            for (int i = 0; i < graph.numV; i++) { thresh.Add(double.Parse(threshold.ReadLine()));}
            List<int> type = new List<int>();
            for (int i = 0; i < graph.numV; i++)
            {
                int flag = int.Parse(nodetype.ReadLine());
                if (flag == 0) { type.Add(0); }
                else if (flag == 1) { type.Add(2); }
                else { type.Add(1); }
            }
            List<double> d = new List<double>{ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
            List<double> cu = new List<double>();
            for (int i = 0; i < graph.numV; i++)
            {
                double t = thresh[i];
                double p = 0.0;
                if (type[i] == 1) { p = System.Math.Pow(t, 0.5); }
                else if (type[i] == 2) { p = t; }
                else { p = 1-System.Math.Pow(1-t, 0.5); }
                foreach( double point in d)
                {
                    if (point < p) continue;
                    cu.Add(point);
                    break;
                }
            }
            List<int> seed = new List<int>();
            for (int i = 0; i < 100; i++) { seed.Add(int.Parse(initial.ReadLine()));}
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 0.8; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 0.8)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                double b = 10;
                while (b <= 10)
                // Build a random hyper graph with mH random hyper edges.
                {
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    Tuple<List<int>, double> realize = bg.Greedy(cu, b, seed);
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    FileStream outfile = new FileStream(filepath+"_5o.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    Console.WriteLine(realize.Item1.Count);

                    Hyper_start = DateTime.Now;
                    Tuple<double, double> results = icm.InfluenceSpread(graph, realize.Item1, 200);
                    Hyper_end = DateTime.Now;
                    writer.Write("Choose time:" + Hyper_time + "\t");
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    writer.Write("Propagation time:" + Hyper_time + "\t");
                    writer.Write("a:" + alpha + "\tb:" + b + "\tave:" + results.Item1 + "\tstd:" + results.Item2+"\tmemory:"+mem+"\n");
                    writer.Flush();
                    writer.Close();
                    b += 10.0;
                }
                alpha += 0.2;
            }
        }
    }
}
