package com.example.openzuma.ui.calendar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.openzuma.data.model.CalendarMonth
import com.example.openzuma.data.model.Schedule
import com.example.openzuma.data.repository.ScheduleRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.util.*
import javax.inject.Inject

@HiltViewModel
class CalendarViewModel @Inject constructor(
    private val repository: ScheduleRepository
) : ViewModel() {
    
    private val _selectedDate = MutableStateFlow(Date())
    val selectedDate: StateFlow<Date> = _selectedDate.asStateFlow()
    
    private val _currentMonth = MutableStateFlow<CalendarMonth?>(null)
    val currentMonth: StateFlow<CalendarMonth?> = _currentMonth.asStateFlow()
    
    private val _schedulesForSelectedDate = MutableStateFlow<List<Schedule>>(emptyList())
    val schedulesForSelectedDate: StateFlow<List<Schedule>> = _schedulesForSelectedDate.asStateFlow()
    
    private val _upcomingSchedules = MutableStateFlow<List<Schedule>>(emptyList())
    val upcomingSchedules: StateFlow<List<Schedule>> = _upcomingSchedules.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    init {
        loadCurrentMonth()
        loadSchedulesForSelectedDate()
        loadUpcomingSchedules()
    }
    
    fun selectDate(date: Date) {
        _selectedDate.value = date
        loadSchedulesForSelectedDate()
    }
    
    fun navigateToPreviousMonth() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance().apply { time = _selectedDate.value }
            calendar.add(Calendar.MONTH, -1)
            _selectedDate.value = calendar.time
            loadMonth(calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH) + 1)
        }
    }
    
    fun navigateToNextMonth() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance().apply { time = _selectedDate.value }
            calendar.add(Calendar.MONTH, 1)
            _selectedDate.value = calendar.time
            loadMonth(calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH) + 1)
        }
    }
    
    fun navigateToToday() {
        _selectedDate.value = Date()
        loadCurrentMonth()
    }
    
    private fun loadCurrentMonth() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance()
            val year = calendar.get(Calendar.YEAR)
            val month = calendar.get(Calendar.MONTH) + 1
            loadMonth(year, month)
        }
    }
    
    private fun loadMonth(year: Int, month: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            
            try {
                // 获取该月的所有日程
                val startDate = Calendar.getInstance().apply {
                    set(year, month - 1, 1, 0, 0, 0)
                    set(Calendar.MILLISECOND, 0)
                }.time
                
                val endDate = Calendar.getInstance().apply {
                    set(year, month - 1, 1, 0, 0, 0)
                    add(Calendar.MONTH, 1)
                }.time
                
                val schedules = repository.getSchedulesBetween(startDate, endDate)
                    .firstOrNull() ?: emptyList()
                
                val calendarMonth = repository.getCalendarForMonth(year, month, schedules)
                _currentMonth.value = calendarMonth
                
            } catch (e: Exception) {
                _errorMessage.value = "加载日历数据失败: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    private fun loadSchedulesForSelectedDate() {
        viewModelScope.launch {
            repository.getSchedulesByDate(_selectedDate.value)
                .catch { e ->
                    _errorMessage.value = "加载日程失败: ${e.message}"
                }
                .collect { schedules ->
                    _schedulesForSelectedDate.value = schedules
                }
        }
    }
    
    private fun loadUpcomingSchedules() {
        viewModelScope.launch {
            val calendar = Calendar.getInstance().apply {
                add(Calendar.DAY_OF_MONTH, 1)
                set(Calendar.HOUR_OF_DAY, 23)
                set(Calendar.MINUTE, 59)
                set(Calendar.SECOND, 59)
                set(Calendar.MILLISECOND, 999)
            }
            
            repository.getUpcomingSchedules(calendar.time)
                .catch { e ->
                    _errorMessage.value = "加载即将到来的日程失败: ${e.message}"
                }
                .collect { schedules ->
                    _upcomingSchedules.value = schedules
                }
        }
    }
    
    fun createSchedule(schedule: Schedule) {
        viewModelScope.launch {
            try {
                repository.createSchedule(schedule)
                loadMonth(
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.YEAR)
                    },
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.MONTH) + 1
                    }
                )
                loadSchedulesForSelectedDate()
                loadUpcomingSchedules()
            } catch (e: Exception) {
                _errorMessage.value = "创建日程失败: ${e.message}"
            }
        }
    }
    
    fun updateSchedule(schedule: Schedule) {
        viewModelScope.launch {
            try {
                repository.updateSchedule(schedule)
                loadMonth(
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.YEAR)
                    },
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.MONTH) + 1
                    }
                )
                loadSchedulesForSelectedDate()
                loadUpcomingSchedules()
            } catch (e: Exception) {
                _errorMessage.value = "更新日程失败: ${e.message}"
            }
        }
    }
    
    fun deleteSchedule(schedule: Schedule) {
        viewModelScope.launch {
            try {
                repository.deleteSchedule(schedule)
                loadMonth(
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.YEAR)
                    },
                    _selectedDate.value.let {
                        val cal = Calendar.getInstance().apply { time = it }
                        cal.get(Calendar.MONTH) + 1
                    }
                )
                loadSchedulesForSelectedDate()
                loadUpcomingSchedules()
            } catch (e: Exception) {
                _errorMessage.value = "删除日程失败: ${e.message}"
            }
        }
    }
    
    fun toggleScheduleCompletion(scheduleId: String, completed: Boolean) {
        viewModelScope.launch {
            try {
                repository.updateCompletionStatus(scheduleId, completed)
                loadSchedulesForSelectedDate()
                loadUpcomingSchedules()
            } catch (e: Exception) {
                _errorMessage.value = "更新状态失败: ${e.message}"
            }
        }
    }
    
    fun clearError() {
        _errorMessage.value = null
    }
}