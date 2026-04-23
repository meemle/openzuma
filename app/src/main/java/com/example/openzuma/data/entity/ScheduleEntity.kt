package com.example.openzuma.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverters
import com.example.openzuma.data.converter.DateConverter
import java.util.Date
import java.util.UUID

@Entity(tableName = "schedules")
@TypeConverters(DateConverter::class)
data class ScheduleEntity(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    
    val title: String,
    val description: String? = null,
    
    val startTime: Date,
    val endTime: Date,
    
    val location: String? = null,
    val color: Int = 0xFF2196F3.toInt(), // 默认蓝色
    
    val isAllDay: Boolean = false,
    val isCompleted: Boolean = false,
    
    val repeatType: String = "none", // none, daily, weekly, monthly, yearly
    val repeatUntil: Date? = null,
    
    val reminderTime: Int = 0, // 提前提醒时间（分钟）
    val reminderSent: Boolean = false,
    
    val createdAt: Date = Date(),
    val updatedAt: Date = Date()
) {
    fun isInProgress(): Boolean {
        val now = Date()
        return now.after(startTime) && now.before(endTime)
    }
    
    fun getDurationInMinutes(): Long {
        return (endTime.time - startTime.time) / (1000 * 60)
    }
}