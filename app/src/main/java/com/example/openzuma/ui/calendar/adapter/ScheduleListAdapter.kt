package com.example.openzuma.ui.calendar.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.openzuma.R
import com.example.openzuma.data.model.Schedule
import java.text.SimpleDateFormat
import java.util.*

class ScheduleListAdapter(
    private val onScheduleClick: (Schedule) -> Unit,
    private val onCompleteClick: (Schedule) -> Unit,
    private val onDeleteClick: (Schedule) -> Unit
) : ListAdapter<Schedule, ScheduleListAdapter.ScheduleViewHolder>(ScheduleDiffCallback()) {

    private val timeFormatter = SimpleDateFormat("HH:mm", Locale.CHINA)
    private val dateTimeFormatter = SimpleDateFormat("MM/dd HH:mm", Locale.CHINA)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ScheduleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_schedule, parent, false)
        return ScheduleViewHolder(view)
    }

    override fun onBindViewHolder(holder: ScheduleViewHolder, position: Int) {
        val schedule = getItem(position)
        holder.bind(schedule)
    }

    inner class ScheduleViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvTitle: TextView = itemView.findViewById(R.id.tv_title)
        private val tvTime: TextView = itemView.findViewById(R.id.tv_time)
        private val tvLocation: TextView = itemView.findViewById(R.id.tv_location)
        private val tvDescription: TextView = itemView.findViewById(R.id.tv_description)
        private val colorIndicator: View = itemView.findViewById(R.id.color_indicator)
        private val btnComplete: ImageButton = itemView.findViewById(R.id.btn_complete)
        private val btnDelete: ImageButton = itemView.findViewById(R.id.btn_delete)

        fun bind(schedule: Schedule) {
            tvTitle.text = schedule.title
            
            // 设置时间显示
            val timeText = if (schedule.isAllDay) {
                "全天"
            } else {
                "${timeFormatter.format(schedule.startTime)} - ${timeFormatter.format(schedule.endTime)}"
            }
            tvTime.text = timeText
            
            // 设置地点
            tvLocation.text = schedule.location ?: "无地点"
            tvLocation.visibility = if (schedule.location.isNullOrEmpty()) View.GONE else View.VISIBLE
            
            // 设置描述
            tvDescription.text = schedule.description ?: "无描述"
            tvDescription.visibility = if (schedule.description.isNullOrEmpty()) View.GONE else View.VISIBLE
            
            // 设置颜色指示器
            colorIndicator.setBackgroundColor(schedule.color)
            
            // 设置完成状态
            if (schedule.isCompleted) {
                btnComplete.setImageResource(R.drawable.ic_check_circle_filled)
                btnComplete.contentDescription = "标记为未完成"
                tvTitle.setTextColor(ContextCompat.getColor(itemView.context, R.color.outline))
                tvTime.setTextColor(ContextCompat.getColor(itemView.context, R.color.outline))
            } else {
                btnComplete.setImageResource(R.drawable.ic_check_circle_outline)
                btnComplete.contentDescription = "标记为已完成"
                tvTitle.setTextColor(ContextCompat.getColor(itemView.context, R.color.onSurface))
                tvTime.setTextColor(ContextCompat.getColor(itemView.context, R.color.onSurfaceVariant))
            }
            
            // 点击事件
            itemView.setOnClickListener {
                onScheduleClick(schedule)
            }
            
            btnComplete.setOnClickListener {
                onCompleteClick(schedule)
            }
            
            btnDelete.setOnClickListener {
                onDeleteClick(schedule)
            }
        }
    }

    class ScheduleDiffCallback : DiffUtil.ItemCallback<Schedule>() {
        override fun areItemsTheSame(oldItem: Schedule, newItem: Schedule): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Schedule, newItem: Schedule): Boolean {
            return oldItem == newItem
        }
    }
}