package com.example.openzuma.ui.calendar.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.openzuma.R
import com.example.openzuma.data.model.ScheduleDay
import java.text.SimpleDateFormat
import java.util.*

class CalendarDayAdapter(
    private val onDayClick: (ScheduleDay) -> Unit
) : ListAdapter<ScheduleDay, CalendarDayAdapter.DayViewHolder>(DayDiffCallback()) {

    private val dayFormatter = SimpleDateFormat("d", Locale.CHINA)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DayViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_calendar_day, parent, false)
        return DayViewHolder(view)
    }

    override fun onBindViewHolder(holder: DayViewHolder, position: Int) {
        val day = getItem(position)
        holder.bind(day)
    }

    inner class DayViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvDayNumber: TextView = itemView.findViewById(R.id.tv_day_number)
        private val dotIndicator: View = itemView.findViewById(R.id.dot_indicator)
        private val dayContainer: View = itemView.findViewById(R.id.day_container)

        fun bind(day: ScheduleDay) {
            val calendar = Calendar.getInstance().apply { time = day.date }
            val dayNumber = calendar.get(Calendar.DAY_OF_MONTH)
            
            tvDayNumber.text = dayNumber.toString()
            
            // 设置样式
            when {
                day.isToday -> {
                    tvDayNumber.setTextColor(
                        ContextCompat.getColor(itemView.context, R.color.white)
                    )
                    dayContainer.setBackgroundResource(R.drawable.bg_calendar_today)
                }
                day.isWeekend -> {
                    tvDayNumber.setTextColor(
                        ContextCompat.getColor(itemView.context, R.color.error)
                    )
                    dayContainer.background = null
                }
                else -> {
                    tvDayNumber.setTextColor(
                        ContextCompat.getColor(itemView.context, R.color.onSurface)
                    )
                    dayContainer.background = null
                }
            }
            
            // 显示是否有日程的指示点
            dotIndicator.visibility = if (day.hasSchedules) View.VISIBLE else View.GONE
            
            // 点击事件
            itemView.setOnClickListener {
                onDayClick(day)
            }
        }
    }

    class DayDiffCallback : DiffUtil.ItemCallback<ScheduleDay>() {
        override fun areItemsTheSame(oldItem: ScheduleDay, newItem: ScheduleDay): Boolean {
            return oldItem.date.time == newItem.date.time
        }

        override fun areContentsTheSame(oldItem: ScheduleDay, newItem: ScheduleDay): Boolean {
            return oldItem.date == newItem.date &&
                   oldItem.hasSchedules == newItem.hasSchedules &&
                   oldItem.isToday == newItem.isToday &&
                   oldItem.isWeekend == newItem.isWeekend
        }
    }
}