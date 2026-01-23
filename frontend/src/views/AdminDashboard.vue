<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">Admin Dashboard</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">Welcome, {{ auth.user?.name }}</div>
        </div>
    </div>
    
    <v-tabs v-model="tab" color="primary">
        <v-tab value="users">Users</v-tab>
        <v-tab value="disciplines">Disciplines</v-tab>
        <v-tab value="semesters">Semesters</v-tab>
        <v-tab value="semesters">Semesters</v-tab>
        <v-tab value="courses">Courses</v-tab>
        <v-tab value="offerings">Course Offerings</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-4">
        <v-window-item value="disciplines">
            <v-card border flat class="pa-4">
                <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-h6">Disciplines</div>
                     <v-btn color="primary" prepend-icon="mdi-plus" @click="openDisciplineDialog()">Add Discipline</v-btn>
                </div>
                
                <v-data-table
                    :headers="disciplineHeaders"
                    :items="disciplines"
                    :loading="loadingDisciplines"
                    density="compact"
                >
                    <template v-slot:item.is_active="{ item }">
                        <v-chip size="x-small" :color="item.is_active ? 'success' : 'error'">
                            {{ item.is_active ? 'Active' : 'Inactive' }}
                        </v-chip>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn icon="mdi-pencil" size="small" variant="text" @click="openDisciplineDialog(item)"></v-btn>
                        <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="confirmDeleteDiscipline(item)"></v-btn>
                    </template>
                </v-data-table>
            </v-card>
        </v-window-item>

        <v-window-item value="users">
            <v-card border flat class="pa-4">
                <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-h6">Users</div>
                     <v-btn color="primary" prepend-icon="mdi-plus" @click="openUserDialog()">Add User</v-btn>
                </div>

                <v-data-table
                    :headers="userHeaders"
                    :items="users"
                    :loading="loadingUsers"
                    density="compact"
                    class="mb-6"
                >
                    <template v-slot:item.is_active="{ item }">
                        <v-chip size="x-small" :color="item.is_active ? 'success' : 'error'">
                            {{ item.is_active ? 'Active' : 'Inactive' }}
                        </v-chip>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn icon="mdi-pencil" size="small" variant="text" @click="openUserDialog(item)"></v-btn>
                        <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deactivateUser(item)"></v-btn>
                    </template>
                </v-data-table>

                <v-divider class="mb-4"></v-divider>

                <div class="text-h6 mb-4">Bulk Upload Users</div>
                <v-file-input
                    v-model="userFile"
                    label="User CSV"
                    accept=".csv"
                    variant="outlined"
                    density="compact"
                ></v-file-input>
                <v-btn color="primary" @click="uploadUsers" :loading="uploadingUsers" :disabled="!userFile">Upload Users</v-btn>
            </v-card>
        </v-window-item>

        <v-window-item value="semesters">
             <v-card border flat class="pa-4">
                <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-h6">Semesters</div>
                     <v-btn color="primary" prepend-icon="mdi-plus" @click="openSemesterDialog()">Add Semester</v-btn>
                </div>
                
                <v-data-table
                    :headers="semesterHeaders"
                    :items="semesters"
                    :loading="loadingSemesters"
                    density="compact"
                >
                    <template v-slot:item.actions="{ item }">
                        <v-btn icon="mdi-pencil" size="small" variant="text" @click="openSemesterDialog(item)"></v-btn>
                        <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteSemester(item)"></v-btn>
                    </template>
                </v-data-table>
            </v-card>
        </v-window-item>

        <v-window-item value="courses">
            <v-card border flat class="pa-4">
                <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-h6">Courses</div>
                     <v-btn color="primary" prepend-icon="mdi-plus" @click="openCourseDialog()">Add Course</v-btn>
                </div>
                
                <v-data-table
                    :headers="courseHeaders"
                    :items="courses"
                    :loading="loadingCourses"
                    density="compact"
                >
                    <template v-slot:item.credits="{ item }">
                        {{ item.lecture_credits }}-{{ item.tutorial_credits }}-{{ item.practice_credits }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn icon="mdi-pencil" size="small" variant="text" @click="openCourseDialog(item)"></v-btn>
                        <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteCourse(item)"></v-btn>
                    </template>
                </v-data-table>
            </v-card>
        </v-window-item>

        <v-window-item value="offerings">
             <v-card border flat class="pa-4">
                <div class="text-h6 mb-4">Bulk Upload Course Offerings</div>
                <v-file-input
                    v-model="offeringFile"
                    label="Offerings CSV"
                    accept=".csv"
                    variant="outlined"
                    density="compact"
                ></v-file-input>
                <div class="text-caption mb-4">
                    Columns: course_code, semester_id, course_name, category, credits (L-T-P), teacher_ids (semicolon sep), [exam_names]...
                </div>
                <v-btn color="primary" @click="uploadOfferings" :loading="uploadingOfferings" :disabled="!offeringFile">Upload Offerings</v-btn>
            </v-card>
        </v-window-item>
    </v-window>

    <!-- Discipline Dialog -->
    <v-dialog v-model="disciplineDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingDiscipline ? 'Edit Discipline' : 'Add Discipline' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="disciplineData.code"
                    label="Code"
                    variant="outlined"
                    :disabled="editingDiscipline"
                ></v-text-field>
                <v-text-field
                    v-model="disciplineData.name"
                    label="Name"
                    variant="outlined"
                ></v-text-field>
                <v-switch
                    v-model="disciplineData.is_active"
                    label="Active"
                    color="primary"
                ></v-switch>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="disciplineDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveDiscipline" :loading="savingDiscipline">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- User Dialog -->
    <v-dialog v-model="userDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingUser ? 'Edit User' : 'Add User' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="userData.id"
                    label="User ID"
                    variant="outlined"
                    :disabled="editingUser"
                ></v-text-field>
                <v-text-field
                    v-model="userData.name"
                    label="Name"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-model="userData.email"
                    label="Email"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-if="!editingUser"
                    v-model="userData.password"
                    label="Password"
                    variant="outlined"
                    type="password"
                ></v-text-field>
                <v-select
                    v-model="userData.role"
                    :items="['student', 'teacher', 'admin', 'alumni']"
                    label="Role"
                    variant="outlined"
                    :disabled="editingUser" 
                ></v-select>
                <v-text-field
                    v-if="userData.role === 'student'"
                    v-model="userData.discipline_code"
                    label="Discipline Code"
                    variant="outlined"
                ></v-text-field>
                 <v-switch
                    v-model="userData.is_active"
                    label="Active"
                    color="primary"
                ></v-switch>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="userDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveUser" :loading="savingUser">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Course Dialog -->
    <v-dialog v-model="courseDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingCourse ? 'Edit Course' : 'Add Course' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="courseData.code"
                    label="Course Code"
                    variant="outlined"
                    :disabled="editingCourse"
                ></v-text-field>
                <v-text-field
                    v-model="courseData.name"
                    label="Course Name"
                    variant="outlined"
                ></v-text-field>
                <v-select
                    v-model="courseData.category"
                    :items="['Core Course', 'Elective', 'MTech Thesis', 'MTech Project']"
                    label="Category"
                    variant="outlined"
                ></v-select>
                <v-row>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.lecture_credits"
                            label="Lecture"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.tutorial_credits"
                            label="Tutorial"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.practice_credits"
                            label="Practice"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="courseDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveCourse" :loading="savingCourse">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Semester Dialog -->
    <v-dialog v-model="semesterDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingSemester ? 'Edit Semester' : 'Add Semester' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-if="!editingSemester"
                    v-model.number="semesterData.id"
                    label="Semester ID"
                    type="number"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-model="semesterData.start_date"
                    label="Start Date"
                    type="date"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-model="semesterData.end_date"
                    label="End Date"
                    type="date"
                    variant="outlined"
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="semesterDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveSemester" :loading="savingSemester">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

     <v-snackbar v-model="snackbar.show" :color="snackbar.color">
        {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const tab = ref('users')

// Semesters
const semesters = ref([])
const loadingSemesters = ref(false)
const semesterDialog = ref(false)
const semesterData = ref({ id: null, start_date: '', end_date: '' })
const editingSemester = ref(false)
const savingSemester = ref(false)

const semesterHeaders = [
    { title: 'Semester ID', key: 'id' },
    { title: 'Start Date', key: 'start_date' },
    { title: 'End Date', key: 'end_date' },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchSemesters = async () => {
    loadingSemesters.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingSemesters.value = false }
}

const openSemesterDialog = (item = null) => {
    if (item) {
        semesterData.value = { ...item }
        editingSemester.value = true
    } else {
        semesterData.value = { id: null, start_date: '', end_date: '' }
        editingSemester.value = false
    }
    semesterDialog.value = true
}

const saveSemester = async () => {
    savingSemester.value = true
    try {
        if (editingSemester.value) {
            await axios.put(`http://localhost:8000/api/v1/academic/semesters/${semesterData.value.id}`, semesterData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/academic/semesters/', semesterData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'Semester saved successfully', color: 'success' }
        semesterDialog.value = false
        fetchSemesters()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save semester: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingSemester.value = false
    }
}

const deleteSemester = async (item) => {
    if (!confirm(`Are you sure you want to delete semester ${item.id}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/academic/semesters/${item.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Semester deleted', color: 'success' }
        fetchSemesters()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to delete: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}


// Disciplines
const disciplines = ref([])
const loadingDisciplines = ref(false)
const disciplineDialog = ref(false)
const disciplineData = ref({ code: '', name: '', is_active: true })
const editingDiscipline = ref(false)
const savingDiscipline = ref(false)

const disciplineHeaders = [
    { title: 'Code', key: 'code' },
    { title: 'Name', key: 'name' },
    { title: 'Status', key: 'is_active' },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchDisciplines = async () => {
    loadingDisciplines.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/disciplines/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        disciplines.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingDisciplines.value = false }
}

const openDisciplineDialog = (item = null) => {
    if (item) {
        disciplineData.value = { ...item }
        editingDiscipline.value = true
    } else {
        disciplineData.value = { code: '', name: '', is_active: true }
        editingDiscipline.value = false
    }
    disciplineDialog.value = true
}

const saveDiscipline = async () => {
    savingDiscipline.value = true
    try {
        if (editingDiscipline.value) {
            await axios.put(`http://localhost:8000/api/v1/disciplines/${disciplineData.value.code}`, disciplineData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/disciplines/', disciplineData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'Discipline saved successfully', color: 'success' }
        disciplineDialog.value = false
        fetchDisciplines()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save discipline: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingDiscipline.value = false
    }
}

const confirmDeleteDiscipline = async (item) => {
    if (!confirm(`Are you sure you want to deactivate discipline ${item.name}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/disciplines/${item.code}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Discipline deactivated', color: 'success' }
        fetchDisciplines()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to deactivate: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}



// Users
const users = ref([])
const loadingUsers = ref(false)
const userDialog = ref(false)
const userData = ref({ id: '', name: '', email: '', role: 'student', discipline_code: null, is_active: true })
const editingUser = ref(false)
const savingUser = ref(false)

const userHeaders = [
    { title: 'ID', key: 'id' },
    { title: 'Name', key: 'name' },
    { title: 'Email', key: 'email' },
    { title: 'Role', key: 'current_role' }, // Assuming backend returns current_role or we need to process roles
    { title: 'Status', key: 'is_active' },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchUsers = async () => {
    loadingUsers.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/users/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        users.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingUsers.value = false }
}

const openUserDialog = (item = null) => {
    if (item) {
        userData.value = { ...item }
        editingUser.value = true
    } else {
        userData.value = { id: '', name: '', email: '', password: 'password123', role: 'student', discipline_code: null, is_active: true }
        editingUser.value = false
    }
    userDialog.value = true
}

const saveUser = async () => {
    savingUser.value = true
    try {
        // Prepare data
        const data = { ...userData.value }
        // Handle roles if creating new user, backend expects roles list
        if (!editingUser.value) {
             data.roles = [data.role]
        }
        
        if (editingUser.value) {
            await axios.put(`http://localhost:8000/api/v1/users/${userData.value.id}`, data, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/users/', data, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'User saved successfully', color: 'success' }
        userDialog.value = false
        fetchUsers()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save user: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingUser.value = false
    }
}

const deactivateUser = async (item) => {
    if (!confirm(`Are you sure you want to deactivate user ${item.name}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/users/${item.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'User deactivated', color: 'success' }
        fetchUsers()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to deactivate: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

const userFile = ref(null)
const uploadingUsers = ref(false)


// Courses
const courses = ref([])
const loadingCourses = ref(false)
const courseDialog = ref(false)
const courseData = ref({ code: '', name: '', category: 'Core Course', lecture_credits: 0, tutorial_credits: 0, practice_credits: 0 })
const editingCourse = ref(false)
const savingCourse = ref(false)

const courseHeaders = [
    { title: 'Code', key: 'code' },
    { title: 'Name', key: 'name' },
    { title: 'Category', key: 'category' },
    { title: 'Credits (L-T-P)', key: 'credits', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchCourses = async () => {
    loadingCourses.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/courses/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        courses.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingCourses.value = false }
}

const openCourseDialog = (item = null) => {
    if (item) {
        courseData.value = { ...item }
        editingCourse.value = true
    } else {
        courseData.value = { code: '', name: '', category: 'Core Course', lecture_credits: 0, tutorial_credits: 0, practice_credits: 0 }
        editingCourse.value = false
    }
    courseDialog.value = true
}

const saveCourse = async () => {
    savingCourse.value = true
    try {
        if (editingCourse.value) {
            await axios.put(`http://localhost:8000/api/v1/courses/${courseData.value.code}`, courseData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/courses/', courseData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'Course saved successfully', color: 'success' }
        courseDialog.value = false
        fetchCourses()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save course: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingCourse.value = false
    }
}

const deleteCourse = async (item) => {
    if (!confirm(`Are you sure you want to delete course ${item.code}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/courses/${item.code}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Course deleted', color: 'success' }
        fetchCourses()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to delete: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

const offeringFile = ref(null)
const uploadingOfferings = ref(false)

const snackbar = ref({ show: false, text: '', color: 'success' })



const uploadUsers = async () => {
    uploadingUsers.value = true
    const formData = new FormData()
    formData.append('file', userFile.value)
    
    try {
        const res = await axios.post('http://localhost:8000/api/v1/users/bulk-upload', formData, {
             headers: { 
                 Authorization: `Bearer ${auth.token}`,
                 'Content-Type': 'multipart/form-data'
             }
        })
        const count = res.data.users_created
        const errors = res.data.errors.length
        snackbar.value = { show: true, text: `Created ${count} users. Errors: ${errors}`, color: errors > 0 ? 'warning' : 'success' }
        userFile.value = null
    } catch (e) {
         snackbar.value = { show: true, text: 'Upload failed', color: 'error' }
    } finally {
        uploadingUsers.value = false
    }
}

const uploadOfferings = async () => {
    uploadingOfferings.value = true
    const formData = new FormData()
    formData.append('file', offeringFile.value)
    
    try {
        const res = await axios.post('http://localhost:8000/api/v1/courses/offerings/bulk-upload', formData, {
             headers: { 
                 Authorization: `Bearer ${auth.token}`,
                 'Content-Type': 'multipart/form-data'
             }
        })
         const count = res.data.offerings_created
        const errors = res.data.errors.length
        snackbar.value = { show: true, text: `Created ${count} offerings. Errors: ${errors}`, color: errors > 0 ? 'warning' : 'success' }
        offeringFile.value = null
    } catch (e) {
         snackbar.value = { show: true, text: 'Upload failed: ' + e.message, color: 'error' }
    } finally {
        uploadingOfferings.value = false
    }
}

onMounted(() => {
    fetchSemesters()
    fetchDisciplines()
    fetchUsers()
    fetchCourses()
})
</script>
