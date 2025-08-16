// Run this in your browser console to fix the Docker port
localStorage.setItem('docker_host', 'tcp://localhost:2375');
console.log('Docker host updated to:', localStorage.getItem('docker_host'));
