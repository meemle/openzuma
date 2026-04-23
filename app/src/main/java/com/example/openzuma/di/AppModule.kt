package com.example.openzuma.di

import android.content.Context
import com.example.openzuma.data.database.AppDatabase
import com.example.openzuma.data.repository.ScheduleRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return AppDatabase.getInstance(context)
    }

    @Provides
    @Singleton
    fun provideScheduleRepository(database: AppDatabase): ScheduleRepository {
        return ScheduleRepository(database.scheduleDao())
    }
}