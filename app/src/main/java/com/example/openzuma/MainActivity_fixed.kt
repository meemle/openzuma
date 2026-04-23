package com.example.openzuma

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
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
        
        // 检查并请求必要的权限
        checkAndRequestPermissions()
        
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
                R.id.navigation_calendar,
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
                R.id.navigation_calendar -> {
                    supportActionBar?.title = getString(R.string.title_calendar)
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
    
    private fun checkAndRequestPermissions() {
        // 检查存储权限（如果需要）
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Settings.System.canWrite(this)) {
                val intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                intent.data = Uri.parse("package:$packageName")
                startActivity(intent)
            }
        }
        
        // 检查相机权限
        val cameraPermission = android.Manifest.permission.CAMERA
        if (ContextCompat.checkSelfPermission(this, cameraPermission) 
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(cameraPermission), 100)
        }
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 100) {
            // 权限处理逻辑
            if (grantResults.isNotEmpty() && grantResults[0] 
                == android.content.pm.PackageManager.PERMISSION_GRANTED) {
                // 权限已授予
            }
        }
    }
    
    override fun onCreateOptionsMenu(menu: android.view.Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: android.view.MenuItem): Boolean {
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