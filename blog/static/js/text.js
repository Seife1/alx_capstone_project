// Add JavaScript code to your HTML to capture the Enter key press and 
// transform it into <p> tags

document.getElementById('content').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const cursorPosition = this.selectionStart;
        const text = this.value;
        const newText = text.substring(0, cursorPosition) + '\n\n<br><p>' + text.substring(cursorPosition) + '</p><br>';
        this.value = newText;
        this.selectionStart = cursorPosition + 9;
        this.selectionEnd = cursorPosition + 9;
    }
});