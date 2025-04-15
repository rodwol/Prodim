import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { format, subDays } from 'date-fns';
import axios from 'axios';
import './LifestyleTracker.css';
import {
  Box, Typography, Paper, Grid, Card, CardContent,
  TextField, Button, MenuItem, Snackbar, Alert,
  CircularProgress, Tabs, Tab, Divider, List, ListItem, ListItemText
} from '@mui/material';

const LifestyleTracker = () => {
  const { user } = useAuth();
  const [lifestyleData, setLifestyleData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [recommendations, setRecommendations] = useState([]);
  const [assessment, setAssessment] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    date: format(new Date(), 'yyyy-MM-dd'),
    physical_activity: 5,
    healthy_diet: 5,
    social_engagement: 5,
    good_sleep: 5,
    smoking: 0,
    alcohol: 0,
    stress: 3,
    notes: ''
  });

  const metrics = [
    { key: 'physical_activity', label: 'Physical Activity', ideal: 'Higher' },
    { key: 'healthy_diet', label: 'Healthy Diet', ideal: 'Higher' },
    { key: 'social_engagement', label: 'Social Engagement', ideal: 'Higher' },
    { key: 'good_sleep', label: 'Quality Sleep', ideal: 'Higher' },
    { key: 'stress', label: 'Stress Level', ideal: 'Lower' },
    { key: 'smoking', label: 'Smoking', ideal: 'Lower' },
    { key: 'alcohol', label: 'Alcohol', ideal: 'Lower' }
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'notes' ? value : Number(value)
    }));
  };

  const fetchLifestyleData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/lifestyle-data/', {
        withCredentials: true
      });
      setLifestyleData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch lifestyle data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/lifestyle-stats/', {
        withCredentials: true
      });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post(
        'http://localhost:8000/api/lifestyle-stats/',
        formData,
        { withCredentials: true }
      );

      setSuccess('Lifestyle data submitted successfully!');
      setFormData({
        date: format(new Date(), 'yyyy-MM-dd'),
        physical_activity: 5,
        healthy_diet: 5,
        social_engagement: 5,
        good_sleep: 5,
        smoking: 0,
        alcohol: 0,
        stress: 3,
        notes: ''
      });

      if (response.data.brain_health_assessment) {
        setAssessment(response.data.brain_health_assessment);
      }
      if (response.data.recommendations) {
        setRecommendations(response.data.recommendations);
      }

      fetchLifestyleData();
      fetchStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit lifestyle data');
    } finally {
      setLoading(false);
    }
  };

  const renderForm = () => (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Record Your Daily Lifestyle
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="date"
              label="Date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {metrics.map(metric => (
            <Grid item xs={12} sm={6} md={4} key={metric.key}>
              <TextField
                select
                fullWidth
                label={metric.label}
                name={metric.key}
                value={formData[metric.key]}
                onChange={handleChange}
              >
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                  <MenuItem key={num} value={num}>
                    {num} {metric.ideal === 'Higher' ? (num >= 7 ? '👍' : num <= 3 ? '👎' : '') : 
                          (num <= 3 ? '👍' : num >= 7 ? '👎' : '')}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          ))}

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Additional Notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
            />
          </Grid>

          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Submit
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );

  const renderTrends = () => {
    if (!stats || !stats.entries.length) return (
      <Typography variant="body1" color="textSecondary">
        No lifestyle data available for trends analysis.
      </Typography>
    );

    const chartData = stats.entries.map(entry => ({
      date: format(new Date(entry.date), 'MMM dd'),
      ...entry
    }));

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            30-Day Trends
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="physical_activity" stroke="#8884d8" activeDot={{ r: 8 }} />
              <Line type="monotone" dataKey="healthy_diet" stroke="#82ca9d" />
              <Line type="monotone" dataKey="social_engagement" stroke="#ffc658" />
              <Line type="monotone" dataKey="good_sleep" stroke="#ff8042" />
              <Line type="monotone" dataKey="stress" stroke="#ff0000" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Averages (Last 30 Days)
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(stats.averages).map(([key, value]) => ({
              name: key.replace('_', ' '),
              value: value.toFixed(1)
            }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Key Metrics
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(stats.averages).map(([key, value]) => (
              <Grid item xs={6} sm={4} key={key}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="textSecondary">
                      {key.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h5">
                      {value.toFixed(1)}
                      <Typography component="span" variant="body2" color="textSecondary">
                        /10
                      </Typography>
                    </Typography>
                    <Typography variant="caption" color={value >= 7 ? 'success.main' : value <= 4 ? 'error.main' : 'warning.main'}>
                      {value >= 7 ? 'Excellent' : value <= 4 ? 'Needs Improvement' : 'Good'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    );
  };

  const renderRecommendations = () => {
    if (!recommendations.length && !assessment) return (
      <Typography variant="body1" color="textSecondary">
        Submit your first lifestyle assessment to get personalized recommendations.
      </Typography>
    );

    return (
      <Grid container spacing={3}>
        {assessment && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Brain Health Assessment
                </Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  {assessment.score}/100
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Cognitive Score: {assessment.cognitive_score}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Last updated: {format(new Date(assessment.date), 'MMMM d, yyyy')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Your Recommendations
          </Typography>
          {recommendations.length > 0 ? (
            <List>
              {recommendations.map((rec, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemText
                    primary={`${rec.priority === 'high' ? '⚠️ ' : ''}${rec.title}`}
                    secondary={rec.description}
                    primaryTypographyProps={{
                      color: rec.priority === 'high' ? 'error.main' : 'text.primary',
                      fontWeight: rec.priority === 'high' ? 'bold' : 'normal'
                    }}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body1" color="textSecondary">
              No specific recommendations at this time.
            </Typography>
          )}
        </Grid>
      </Grid>
    );
  };

  useEffect(() => {
    fetchLifestyleData();
    fetchStats();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Lifestyle Tracker
      </Typography>
      <Typography variant="body1" paragraph>
        Track your daily habits and see how they impact your brain health over time.
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="New Entry" />
        <Tab label="Trends & Stats" />
        <Tab label="Recommendations" />
      </Tabs>

      <Divider sx={{ mb: 3 }} />

      {activeTab === 0 && renderForm()}
      {activeTab === 1 && renderTrends()}
      {activeTab === 2 && renderRecommendations()}

      <Snackbar open={!!error} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar open={!!success} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LifestyleTracker;
