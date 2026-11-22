// Manage Jenkins -> Script Console: tek bir job'un eski build'lerini siler.
// jobName ve maxBuildsToKeep değerlerini değiştirerek kullanın.

def jobName = 'shared-library-demo'
def maxBuildsToKeep = 2

def job = Jenkins.instance.getItemByFullName(jobName, Job.class)
if (job == null) {
    println "Job bulunamadı: " + jobName
    return
}
def builds = job.getBuilds()
println jobName + ": " + builds.size() + " build var, son " + maxBuildsToKeep + " tanesi kalacak"
builds.drop(maxBuildsToKeep).each { b ->
    println "  Silindi: #" + b.number
    b.delete()
}
println "Kalan build: " + job.getBuilds().size()
