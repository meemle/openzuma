package com.example.openzuma.data.model

import java.util.*

data class Schedule(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val description: String? = null,
    val startTime: Date,
    val endTime: Date,
    val location: String? = null,
    val color: Int = 0xFF2196F3.toInt(),
    val isAllDay: Boolean = false,
    val isCompleted: Boolean = false,
    val repeatType: String = "none",
    val reminderTime: Int = 0, // 提前提醒时间（分钟）
    
    // 计算属性
    val isInProgress: Boolean
        get() {
            val now = Date()
            return now.after(startTime) && now.before(endTime)
        }
    
    val durationInMinutes: Long
        get() = (endTime.time - startTime.time) / (1000 * 60)
    
    companion object {
        fun fromEntity(entity: ScheduleEntity): Schedule {
            return Schedule(
                id = entity.id,
                title = entity.title,
                description = entity.description,
                startTime = entity.startTime,
                endTime = entity.endTime,
                location = entity.location,
                color = entity.color,
                isAllDay = entity.isAllDay,
                isCompleted = entity.isCompleted,
                repeatType = entity.repeatType,
                reminderTime = entity.reminderTime
            )
        }
    }
    
    fun toEntity(): ScheduleEntity {
        return ScheduleEntity(
            id = id,
            title = title,
            description = description,
            startTime = startTime,
            endTime = endTime,
            location = location,
            color = color,
            isAllDay = isAllDay,
            isCompleted = isCompleted,
            repeatType = repeatType,
            reminderTime = reminderTime
        )
    }
}

data class ScheduleDay(
    val date: Date,
    val schedules: List<Schedule> = emptyList(),
    val hasSchedules: Boolean = schedules.isNotEmpty(),
    val isToday: Boolean = false,
    val isWeekend: Boolean = false
)

data class CalendarMonth(
    val year: Int,
    val month: Int, // 1-12
    val weeks: List<List<ScheduleDay>> = emptyList(),
    val weekDays: List<String> = listOf("日", "一", "二", "三", "四", "五", "六")
)