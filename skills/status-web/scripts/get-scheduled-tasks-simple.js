// 获取定时任务数据（从OpenClaw实际调度系统读取）
async function getScheduledTasksSimple() {
    try {
        const fs = require('fs');
        const path = require('path');
        
        // 读取OpenClaw实际jobs.json
        const openclawJobsPath = '/root/.openclaw/cron/jobs.json';
        const cronJobsPath = '/root/.openclaw/workspace/cron-jobs-updated.json';
        
        let tasks = [];
        
        // 优先从OpenClaw实际调度系统读取
        if (fs.existsSync(openclawJobsPath)) {
            const data = JSON.parse(fs.readFileSync(openclawJobsPath, 'utf8'));
            tasks = data.jobs || [];
        } else if (fs.existsSync(cronJobsPath)) {
            // 回退到配置文件
            const data = JSON.parse(fs.readFileSync(cronJobsPath, 'utf8'));
            tasks = data.jobs || [];
        }
        
        // 格式化任务数据
        return tasks.filter(job => job.enabled).map(job => {
            const state = job.state || {};
            
            // 转换时间戳为可读格式
            const lastRun = state.lastRunAtMs 
                ? new Date(state.lastRunAtMs).toLocaleString('zh-CN') 
                : 'never';
            
            const nextRun = state.nextRunAtMs 
                ? new Date(state.nextRunAtMs).toLocaleString('zh-CN') 
                : 'unknown';
            
            return {
                name: job.name,
                schedule: job.schedule?.expr || 'unknown',
                next_run: nextRun,
                last_run: lastRun,
                status: state.lastStatus || 'unknown',
                duration: state.lastDurationMs 
                    ? `${(state.lastDurationMs / 1000).toFixed(1)}s` 
                    : '-',
                consecutive_errors: state.consecutiveErrors || 0
            };
        });
    } catch (error) {
        console.error('获取定时任务失败:', error);
        return [];
    }
}

module.exports = { getScheduledTasksSimple };
