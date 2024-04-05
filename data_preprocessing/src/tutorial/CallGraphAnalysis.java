package tutorial;

import soot.*;
import soot.jimple.*;
import soot.jimple.toolkits.callgraph.*;

import java.util.*;

public class CallGraphAnalysis extends SceneTransformer {
    private final List<SootMethod> _entryPoints;

    public CallGraphAnalysis(List<SootMethod> entryPoints) {
        _entryPoints = entryPoints;
    }

    @Override
    protected void internalTransform(String phaseName, Map<String, String> options) {
        CallGraph cg = Scene.v().getCallGraph();
        //printPartialCallGraph(cg);
        printCallGraph(cg);
    }

    // private void printPartialCallGraph(CallGraph cg) {
    //     // Print only the entry-points and the methods they invoke.
    //     for (SootMethod entryPoint : _entryPoints) {
    //         System.out.println("Entry-point: " + entryPoint);

    //         Iterator<Edge> outEdges = cg.edgesOutOf(entryPoint);

    //         while (outEdges.hasNext()) {
    //             Edge outEdge = outEdges.next();
    //             SootMethod invokedMethod = outEdge.getTgt().method();
    //             System.out.println("  invokes " + invokedMethod);
    //         }
    //     }
    // }
      private void printCallGraph(CallGraph cg) {
        // A set to keep track of visited methods to avoid infinite recursion on cyclic graphs
        Set<SootMethod> visited = new HashSet<>();

        // Start from each entry point and explore
        for (SootMethod entryPoint : _entryPoints) {
            System.out.println("Entry-point: " + entryPoint);
            printCallGraphDFS(cg, entryPoint, 1, visited); // Start with depth level 1
        }
    }

    private void printCallGraphDFS(CallGraph cg, SootMethod method, int depth, Set<SootMethod> visited) {
        // If the method has already been visited, stop the recursion
        if (!visited.add(method)) {
            return;
        }

        // Iterate over all methods that the current method invokes
        Iterator<Edge> outEdges = cg.edgesOutOf(method);
        while (outEdges.hasNext()) {
            Edge outEdge = outEdges.next();
            SootMethod invokedMethod = outEdge.getTgt().method();
            System.out.println(getIndentString(depth) + depth + ": invokes " + invokedMethod);
            // Recurse into the next level
            printCallGraphDFS(cg, invokedMethod, depth + 1, visited);
        }
    }

    // Helper method to create an indent string based on the depth level
    private String getIndentString(int depth) {
        char[] indent = new char[depth * 2]; // Multiply by 2 (or any other number) to increase indent size per level
        Arrays.fill(indent, ' '); // Fill with spaces
        return new String(indent);
    }

}

