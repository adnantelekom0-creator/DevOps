// Jenkins Script Console: System & Node Inspector
// Run this via Manage Jenkins -> Script Console

println "=== JENKINS SISTEM BILGILERI ==="
println "Jenkins Versiyonu: " + Jenkins.instance.version
println "Root URL:          " + Jenkins.instance.rootUrl
println "Num Executors:     " + Jenkins.instance.numExecutors

println "\n=== KAYITLI AJANLAR (NODES) ==="
Jenkins.instance.nodes.each { node ->
    def comp = node.toComputer()
    println "Ajan: " + node.displayName + " | Online: " + comp.isOnline() + " | Executors: " + comp.numExecutors
}

println "\n=== IS KUYRUGU (QUEUE) ==="
def queue = Jenkins.instance.queue
println "Kuyruktaki Is Sayisi: " + queue.items.length
queue.items.each { item ->
    println "- " + item.task.name + " (Neden: " + item.why + ")"
}
