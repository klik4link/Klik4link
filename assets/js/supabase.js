const SUPABASE_URL = "https://lprwxtzqrfyicmknxeau.supabase.co/rest/v1/";

const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxwcnd4dHpxcmZ5aWNta254ZWF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1MjYyNjQsImV4cCI6MjA5OTEwMjI2NH0.oCK3RT6v0sXHo-bK9u-YbFkJOZi2Q7qmJABkZe1omgg";


const supabaseClient =
supabase.createClient(
SUPABASE_URL,
SUPABASE_KEY
);
