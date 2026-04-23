package com.example.openzuma.data.repository

import com.example.openzuma.data.dao.ScheduleDao
import com.example.openzuma.data.model.Schedule
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ScheduleRepository @Inject constructor(
    private val scheduleDao: ScheduleDao
) {
    
    suspend fun createSchedule(schedule: Schedule) {
        scheduleDao.insert(schedule.toEntity())
    }
    
    suspend fun updateSchedule(schedule: Schedule) {
        scheduleDao.update(schedule.toEntity())
    }
    
    suspend fun deleteSchedule(schedule: Schedule) {
        scheduleDao.delete(schedule.toEntity())
    }
    
    suspend fun getScheduleById(id: String): Schedule? {
        return scheduleDao.getById(id)?.let { Schedule.fromEntity(it) }
    }
    
    fun getSchedulesBetween(startDate: Date, endDate: Date): Flow<List<Schedule>> {
        return scheduleDao.getSchedulesBetween(startDate, endDate).map { entities ->
            entities.map { Schedule.fromEntity(it) }
        }
    }
    
    fun getSchedulesByDate(date: Date): Flow<List<Schedule>> {
        return scheduleDao.getSchedulesByDate(date).map { entities ->
            entities.map { Schedule.fromEntity(it) }
        }
    }
    
    fun getUpcomingSchedules(endOfDay: Date): Flow<List<Schedule>> {
        return scheduleDao.getUpcomingSchedules(endOfDay).map { entities ->
            entities.map { Schedule.fromEntity(it) }
        }
    }
    
    fun getCompletedSchedules(): Flow<List<Schedule>> {
        return scheduleDao.getCompletedSchedules().map { entities ->
            entities.map { Schedule.fromEntity(it) }
        }
    }
    
    suspend fun searchSchedules(query: String): List<Schedule> {
        return scheduleDao.searchSchedules(query).map { Schedule.fromEntity(it) }
    }
    
    suspend fun updateCompletionStatus(scheduleId: String, completed: Boolean) {
        scheduleDao.updateCompletionStatus(scheduleId, completed)
    }
    
    suspend fun deleteOldSchedules(beforeDate: Date) {
        scheduleDao.deleteOldSchedules(beforeDate)
    }
    
    suspend fun getPendingCountBetween(startDate: Date, endDate: Date): Int {
        return scheduleDao.getPendingCountBetween(startDate, endDate)
    }
    
    // 日历相关辅助方法
    fun getCalendarForMonth(year: Int, month: Int, schedules: List<Schedule>): CalendarMonth {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.YEAR, year)
            set(Calendar.MONTH, month - 1)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        
        val today = Calendar.getInstance()
        val todayYear = today.get(Calendar.YEAR)
        val todayMonth = today.get(Calendar.MONTH) + 1
        val todayDay = today.get(Calendar.DAY_OF_MONTH)
        
        val weeks = mutableListOf<List<ScheduleDay>>()
        val firstDayOfWeek = calendar.get(Calendar.DAY_OF_WEEK) // 1=Sunday, 2=Monday, etc.
        
        // 调整到本月第一天所在的周的第一天
        calendar.add(Calendar.DAY_OF_MONTH, -(firstDayOfWeek - 1))
        
        repeat(6) { weekIndex ->
            val weekDays = mutableListOf<ScheduleDay>()
            repeat(7) { dayIndex ->
                val currentDate = calendar.time
                val currentYear = calendar.get(Calendar.YEAR)
                val currentMonth = calendar.get(Calendar.MONTH) + 1
                val currentDay = calendar.get(Calendar.DAY_OF_MONTH)
                val dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
                
                val daySchedules = schedules.filter { schedule ->
                    val scheduleCal = Calendar.getInstance().apply { time = schedule.startTime }
                    scheduleCal.get(Calendar.YEAR) == currentYear &&
                    scheduleCal.get(Calendar.MONTH) + 1 == currentMonth &&
                    scheduleCal.get(Calendar.DAY_OF_MONTH) == currentDay
                }
                
                val isToday = currentYear == todayYear && 
                              currentMonth == todayMonth && 
                              currentDay == todayDay
                val isWeekend = dayOfWeek == Calendar.SATURDAY || dayOfWeek == Calendar.SUNDAY
                
                weekDays.add(ScheduleDay(
                    date = currentDate,
                    schedules = daySchedules,
                    isToday = isToday,
                    isWeekend = isWeekend
                ))
                
                calendar.add(Calendar.DAY_OF_MONTH, 1)
            }
            weeks.add(weekDays)
        }
        
        return CalendarMonth(year, month, weeks)
    }
}