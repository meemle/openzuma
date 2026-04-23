package com.example.openzuma.data.dao

import androidx.room.*
import com.example.openzuma.data.entity.ScheduleEntity
import java.util.Date

@Dao
interface ScheduleDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(schedule: ScheduleEntity)
    
    @Update
    suspend fun update(schedule: ScheduleEntity)
    
    @Delete
    suspend fun delete(schedule: ScheduleEntity)
    
    @Query("SELECT * FROM schedules WHERE id = :id")
    suspend fun getById(id: String): ScheduleEntity?
    
    @Query("SELECT * FROM schedules WHERE startTime >= :startDate AND startTime < :endDate ORDER BY startTime ASC")
    suspend fun getSchedulesBetween(startDate: Date, endDate: Date): List<ScheduleEntity>
    
    @Query("SELECT * FROM schedules WHERE DATE(startTime / 1000, 'unixepoch', 'localtime') = DATE(:date / 1000, 'unixepoch', 'localtime') ORDER BY startTime ASC")
    suspend fun getSchedulesByDate(date: Date): List<ScheduleEntity>
    
    @Query("SELECT * FROM schedules WHERE isCompleted = 0 AND startTime < :endOfDay ORDER BY startTime ASC LIMIT 10")
    suspend fun getUpcomingSchedules(endOfDay: Date): List<ScheduleEntity>
    
    @Query("SELECT * FROM schedules WHERE isCompleted = 1 ORDER BY endTime DESC LIMIT 50")
    suspend fun getCompletedSchedules(): List<ScheduleEntity>
    
    @Query("SELECT * FROM schedules WHERE title LIKE '%' || :query || '%' OR description LIKE '%' || :query || '%' ORDER BY startTime DESC")
    suspend fun searchSchedules(query: String): List<ScheduleEntity>
    
    @Query("UPDATE schedules SET isCompleted = :completed WHERE id = :id")
    suspend fun updateCompletionStatus(id: String, completed: Boolean)
    
    @Query("DELETE FROM schedules WHERE startTime < :date")
    suspend fun deleteOldSchedules(date: Date)
    
    @Query("SELECT COUNT(*) FROM schedules WHERE isCompleted = 0 AND startTime >= :startDate AND startTime < :endDate")
    suspend fun getPendingCountBetween(startDate: Date, endDate: Date): Int
}