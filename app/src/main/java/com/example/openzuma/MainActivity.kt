package com.example.openzuma

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.example.openzuma.databinding.ActivityMainBinding
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var navController: NavController
    private lateinit var appBarConfiguration: AppBarConfiguration

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setSupportActionBar(binding.toolbar)
        
        // 设置导航控制器
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController
        
        // 配置底部导航
        val bottomNavView: BottomNavigationView = binding.bottomNavView
        bottomNavView.setupWithNavController(navController)
        
        // 配置AppBar
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.navigation_home,
                R.id.navigation_discover,
                R.id.navigation_camera,
                R.id.navigation_notifications,
                R.id.navigation_profile
            )
        )
        
        setupActionBarWithNavController(navController, appBarConfiguration)
        
        // 监听导航变化
        navController.addOnDestinationChangedListener { _, destination, _ ->
            when (destination.id) {
                R.id.navigation_home -> {
                    supportActionBar?.title = getString(R.string.title_home)
                }
                R.id.navigation_discover -> {
                    supportActionBar?.title = getString(R.string.title_discover)
                }
                R.id.navigation_camera -> {
                    supportActionBar?.title = getString(R.string.title_camera)
                }
                R.id.navigation_notifications -> {
                    supportActionBar?.title = getString(R.string.title_notifications)
                }
                R.id.navigation_profile -> {
                    supportActionBar?.title = getString(R.string.title_profile)
                }
            }
        }
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_settings -> {
                // 跳转到设置页面
                navController.navigate(R.id.action_global_settingsFragment)
                true
            }
            R.id.action_search -> {
                // 打开搜索
                navController.navigate(R.id.action_global_searchFragment)
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
}