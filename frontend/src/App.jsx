import { useState } from 'react'
import Box from '@mui/material/Box'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'
import HomeIcon from '@mui/icons-material/Home'
import SettingsIcon from '@mui/icons-material/Settings'
import InfoIcon from '@mui/icons-material/Info'
import ContactMailIcon from '@mui/icons-material/ContactMail'
import AssessmentIcon from '@mui/icons-material/Assessment'
import Report from './Report'

const menuItems = [
  { id: 'home', label: 'Home', icon: <HomeIcon />, content: 'Welcome to the Home page. This is the main landing area of your application.' },
  { id: 'about', label: 'About', icon: <InfoIcon />, content: 'About page content. Learn more about this application and its features.' },
  { id: 'contact', label: 'Contact', icon: <ContactMailIcon />, content: 'Contact page content. Reach out to us for any questions or support.' },
  { id: 'report', label: 'Report', icon: <AssessmentIcon />, component: Report },
  { id: 'settings', label: 'Settings', icon: <SettingsIcon />, content: 'Settings page content. Configure your application preferences here.' },
]

export default function App() {
  const [selectedId, setSelectedId] = useState('home')

  const selectedItem = menuItems.find((item) => item.id === selectedId)

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar - 20% width */}
      <Box
        sx={{
          width: '20%',
          bgcolor: 'grey.100',
          borderRight: 1,
          borderColor: 'divider',
          overflow: 'auto',
        }}
      >
        <Typography variant="h6" sx={{ p: 2, fontWeight: 'bold' }}>
          Menu
        </Typography>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.id}
              selected={selectedId === item.id}
              onClick={() => setSelectedId(item.id)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Box>

      {/* Content - 80% width */}
      <Box
        sx={{
          width: '80%',
          p: 3,
          overflow: 'auto',
        }}
      >
        {selectedItem?.component ? (
          <selectedItem.component />
        ) : (
          <>
            <Typography variant="h4" gutterBottom>
              {selectedItem?.label}
            </Typography>
            <Typography variant="body1">{selectedItem?.content}</Typography>
          </>
        )}
      </Box>
    </Box>
  )
}
