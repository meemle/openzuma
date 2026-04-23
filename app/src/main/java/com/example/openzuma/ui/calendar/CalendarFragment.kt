package com.example.openzuma.ui.calendar

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.openzuma.R
import com.example.openzuma.databinding.FragmentCalendarBinding
import com.example.openzuma.ui.calendar.adapter.CalendarDayAdapter
import com.example.openzuma.ui.calendar.adapter.ScheduleListAdapter
import com.google.android.material.datepicker.MaterialDatePicker
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class CalendarFragment : Fragment() {

    private var _binding: FragmentCalendarBinding? = null
    private val binding get() = _binding!!

    private val viewModel: CalendarViewModel by viewModels()

    private lateinit var calendarDayAdapter: CalendarDayAdapter
    private lateinit var scheduleListAdapter: ScheduleListAdapter

    private val dateFormatter = SimpleDateFormat("yyyy年MM月", Locale.CHINA)
    private val dayDateFormatter = SimpleDateFormat("M月d日", Locale.CHINA)
    private val weekdayFormatter = SimpleDateFormat("EEEE", Locale.CHINA)
    private val datePickerFormatter = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCalendarBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupAdapters()
        setupObservers()
        setupClickListeners()
    }

    private fun setupAdapters() {
        // 日历网格适配器
        calendarDayAdapter = CalendarDayAdapter(
            onDayClick = { scheduleDay ->
                viewModel.selectDate(scheduleDay.date)
            }
        )

        binding.rvCalendarGrid.apply {
            layoutManager = GridLayoutManager(requireContext(), 7)
            adapter = calendarDayAdapter
            setHasFixedSize(true)
        }

        // 日程列表适配器
        scheduleListAdapter = ScheduleListAdapter(
            onScheduleClick = { schedule ->
                navigateToScheduleDetail(schedule)
            },
            onCompleteClick = { schedule ->
                viewModel.toggleScheduleCompletion(schedule.id, !schedule.isCompleted)
            },
            onDeleteClick = { schedule ->
                showDeleteConfirmDialog(schedule)
            }
        )

        binding.rvScheduleList.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = scheduleListAdapter
            setHasFixedSize(true)
        }
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.currentMonth.collectLatest { calendarMonth ->
                calendarMonth?.let {
                    updateMonthHeader(it)
                    calendarDayAdapter.submitList(it.weeks.flatten())
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.selectedDate.collectLatest { date ->
                updateSelectedDateHeader(date)
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.schedulesForSelectedDate.collectLatest { schedules ->
                updateScheduleList(schedules)
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.isLoading.collectLatest { isLoading ->
                binding.progressBar.isVisible = isLoading
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.errorMessage.collectLatest { error ->
                error?.let {
                    Toast.makeText(requireContext(), error, Toast.LENGTH_SHORT).show()
                    viewModel.clearError()
                }
            }
        }
    }

    private fun setupClickListeners() {
        binding.btnPrevMonth.setOnClickListener {
            viewModel.navigateToPreviousMonth()
        }

        binding.btnNextMonth.setOnClickListener {
            viewModel.navigateToNextMonth()
        }

        binding.btnToday.setOnClickListener {
            viewModel.navigateToToday()
        }

        binding.btnAddSchedule.setOnClickListener {
            navigateToAddSchedule()
        }

        binding.tvSelectedDate.setOnClickListener {
            showDatePicker()
        }
    }

    private fun updateMonthHeader(calendarMonth: CalendarMonth) {
        binding.tvMonthYear.text = "${calendarMonth.year}年${calendarMonth.month}月"
    }

    private fun updateSelectedDateHeader(date: Date) {
        val calendar = Calendar.getInstance().apply { time = date }
        val today = Calendar.getInstance()
        
        val dayText = if (calendar.get(Calendar.YEAR) == today.get(Calendar.YEAR) &&
            calendar.get(Calendar.MONTH) == today.get(Calendar.MONTH) &&
            calendar.get(Calendar.DAY_OF_MONTH) == today.get(Calendar.DAY_OF_MONTH)) {
            "今天"
        } else {
            weekdayFormatter.format(date)
        }
        
        binding.tvSelectedDate.text = "$dayText, ${dayDateFormatter.format(date)}"
    }

    private fun updateScheduleList(schedules: List<com.example.openzuma.data.model.Schedule>) {
        scheduleListAdapter.submitList(schedules)
        binding.tvScheduleCount.text = "${schedules.size}个日程"
        
        val isEmpty = schedules.isEmpty()
        binding.emptyState.isVisible = isEmpty
        binding.rvScheduleList.isVisible = !isEmpty
    }

    private fun showDatePicker() {
        val datePicker = MaterialDatePicker.Builder.datePicker()
            .setTitleText("选择日期")
            .setSelection(viewModel.selectedDate.value.time)
            .build()

        datePicker.addOnPositiveButtonClickListener { selection ->
            val selectedDate = Date(selection)
            viewModel.selectDate(selectedDate)
            
            // 如果选择的是其他月份的日期，切换到该月份
            val calendar = Calendar.getInstance().apply { time = selectedDate }
            val currentCalendar = Calendar.getInstance().apply { time = viewModel.selectedDate.value }
            
            if (calendar.get(Calendar.MONTH) != currentCalendar.get(Calendar.MONTH) ||
                calendar.get(Calendar.YEAR) != currentCalendar.get(Calendar.YEAR)) {
                viewModel.loadMonth(
                    calendar.get(Calendar.YEAR),
                    calendar.get(Calendar.MONTH) + 1
                )
            }
        }

        datePicker.show(parentFragmentManager, "DATE_PICKER")
    }

    private fun navigateToAddSchedule() {
        val action = CalendarFragmentDirections.actionCalendarFragmentToScheduleEditFragment(
            selectedDate = viewModel.selectedDate.value.time
        )
        findNavController().navigate(action)
    }

    private fun navigateToScheduleDetail(schedule: com.example.openzuma.data.model.Schedule) {
        val action = CalendarFragmentDirections.actionCalendarFragmentToScheduleDetailFragment(
            scheduleId = schedule.id
        )
        findNavController().navigate(action)
    }

    private fun showDeleteConfirmDialog(schedule: com.example.openzuma.data.model.Schedule) {
        androidx.appcompat.app.AlertDialog.Builder(requireContext())
            .setTitle("删除日程")
            .setMessage("确定要删除「${schedule.title}」吗？")
            .setPositiveButton("删除") { _, _ ->
                viewModel.deleteSchedule(schedule)
            }
            .setNegativeButton("取消", null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        fun newInstance() = CalendarFragment()
    }
}