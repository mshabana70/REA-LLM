package tutorial;

import soot.*;

import java.io.File;
import java.io.PrintStream;
import java.util.*;

public class SootTutorial {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("Usage: SootTutorial <APK file>");
            return;
        }

        String apkFile = args[0];
        System.out.println("Analyzing APK: " + apkFile);

        // Initialize Soot options.
        initializeSoot(apkFile);

        // Naively compute entry-points (i.e. where execution begins) for the call graph.
        List<SootMethod> entryPoints = naivelyComputeEntryPoints();
        Scene.v().setEntryPoints(entryPoints);

        // Add our CallGraphAnalysis as a post-callgraph phase.
        PackManager.v().getPack("wjtp").add(new Transform("wjtp.CallGraphAnalysis",
                new CallGraphAnalysis(entryPoints)));

        // Run everything (includes call graph generation and our analysis).
        PackManager.v().runPacks();
    }

    public static void initializeSoot(String apkFile) {
        soot.G.reset();

        // Source format: APK
        soot.options.Options.v().set_src_prec(soot.options.Options.src_prec_apk);

        // Note: turning off Soot's output format leads to undesired "optimizations" where
        // common external third-party package names are excluded.
        soot.options.Options.v().set_output_format(
                soot.options.Options.output_format_force_dex);

        soot.options.Options.v().set_process_multiple_dex(true);
        soot.options.Options.v().set_soot_classpath("/scratch/cg4053/soot/soot-4.4.0-jar-with-dependencies.jar");
        soot.options.Options.v().set_android_jars("/scratch/cg4053/Android_platform/android-platforms");
        soot.options.Options.v().set_prepend_classpath(true);
        soot.options.Options.v().set_allow_phantom_refs(true);
        soot.options.Options.v().set_force_overwrite(true);
        soot.options.Options.v().set_whole_program(true);
        soot.options.Options.v().setPhaseOption("cg", "callgraph-tags:true");
        soot.options.Options.v().setPhaseOption("cg.spark", "on");
        soot.options.Options.v().setPhaseOption("cg.spark", "string-constants:true");

        // Suppress output (comment out if you want to see the vast amounts of output
        // Soot produces).
        try {
            G.v().out = new PrintStream(new File("/dev/null"));
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Exclude certain packages from the analysis for better performance.
        List<String> excludeList = new LinkedList<String>();
        excludeList.add("java.");
        excludeList.add("sun.misc.");
        excludeList.add("android.");
        excludeList.add("com.android.");
        excludeList.add("dalvik.system.");
        excludeList.add("org.apache.");
        excludeList.add("soot.");
        excludeList.add("javax.servlet.");
        soot.options.Options.v().set_exclude(excludeList);
        soot.options.Options.v().set_no_bodies_for_excluded(true);

        // Add code to be analyzed.
        List<String> inputCode = new ArrayList<String>();
        inputCode.add(apkFile);
        soot.options.Options.v().set_process_dir(inputCode);

        // Loads classes and creates the class hierarchy.
        Scene.v().loadNecessaryClasses();
    }

    public static List<SootMethod> naivelyComputeEntryPoints() {
        // Naively compute entry-points by adding all overridden methods of subclasses
        // of Activity in the application.  The class hierarchy (i.e. which tracks the
        // relationships between classes and subclasses) should have been computed in
        // initializeSoot().
        List<SootMethod> entryPoints = new ArrayList<SootMethod>();

        SootClass activityClass = Scene.v().getSootClass("android.app.Activity");
        Hierarchy cha = Scene.v().getActiveHierarchy();

        // Look at all subclasses of Activity.
        for (SootClass activitySubClass : cha.getSubclassesOf(activityClass)) {
            // Make sure this is an application class and not a framework one.
            if (!activitySubClass.isApplicationClass()) {
                continue;
            }

            // Look at the methods in this Activity subclass.
            for (SootMethod activityMethod : activitySubClass.getMethods()) {
                // If this method overrides a method from the parent Activity class,
                // consider this an entry-point to the application.
                if (activityClass.declaresMethod(activityMethod.getSubSignature())) {
                    entryPoints.add(activityMethod);
                }
            }
        }

        return entryPoints;
    }
}

