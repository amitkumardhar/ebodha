<template>
    <v-card border flat class="pa-4 mb-4">
        <div class="text-h6 mb-4">Course Offerings Management</div>

        <v-row class="mb-4">
            <v-col cols="12" md="6">
                <v-select
                    v-model="selectedOfferingSemester"
                    :items="semesters"
                    item-title="name"
                    item-value="id"
                    label="Filter by Semester"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @update:model-value="fetchOfferings"
                ></v-select>
            </v-col>
            <v-col cols="12" md="6" class="text-right">
                <v-btn
                    color="primary"
                    prepend-icon="mdi-download"
                    variant="text"
                    class="mr-2"
                    @click="downloadOfferings"
                    :disabled="!selectedOfferingSemester"
                >
                    Download CSV
                </v-btn>
                <v-btn
                    color="primary"
                    prepend-icon="mdi-plus"
                    @click="openOfferingDialog()"
                    :disabled="!selectedOfferingSemester"
                >
                    Add Offering
                </v-btn>
            </v-col>
        </v-row>

        <v-text-field
            v-if="selectedOfferingSemester"
            v-model="searchOfferings"
            prepend-inner-icon="mdi-magnify"
            label="Search Offerings"
            variant="outlined"
            density="compact"
            hide-details
            class="mb-4"
            clearable
        ></v-text-field>

        <v-data-table
            v-if="selectedOfferingSemester"
            :headers="offeringHeaders"
            :items="offerings"
            :loading="loadingOfferings"
            :search="searchOfferings"
            density="compact"
        >
            <template v-slot:item.examinations="{ item }">
                <v-chip
                    v-for="exam in item.examinations"
                    :key="exam.id || exam.name"
                    size="x-small"
                    class="mr-1 mb-1"
                    variant="outlined"
                >
                    {{ exam.name }} ({{ exam.max_marks }})
                </v-chip>
                <span v-if="!item.examinations?.length" class="text-caption text-medium-emphasis">No exams</span>
            </template>
            <template v-slot:item.teachers="{ item }">
                <div v-for="teacher in item.teachers" :key="teacher.teacher_id" class="text-caption">
                    {{ teacher.teacher_name }}
                </div>
                <span v-if="!item.teachers?.length" class="text-caption text-medium-emphasis">No teachers</span>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="small" variant="text" @click="openOfferingDialog(item)"></v-btn>
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteOffering(item)"></v-btn>
            </template>
        </v-data-table>
        <div v-else class="text-center py-10 text-medium-emphasis">
            Please select a semester to manage course offerings
        </div>
    </v-card>

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

    <!-- Offering Dialog -->
    <v-dialog v-model="offeringDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingOffering ? 'Edit Offering' : 'Add Course Offering' }}</v-card-title>
            <v-card-text>
                <v-select
                    v-model="offeringData.semester_id"
                    :items="semesters"
                    item-title="name"
                    item-value="id"
                    label="Semester"
                    variant="outlined"
                    disabled
                ></v-select>
                <v-select
                    v-model="offeringData.course_code"
                    :items="courses"
                    item-title="code"
                    item-value="code"
                    label="Course"
                    variant="outlined"
                    :disabled="editingOffering"
                >
                    <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props" :subtitle="item.raw.name"></v-list-item>
                    </template>
                </v-select>

                <div class="mt-4">
                    <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-subtitle-2">Examinations</div>
                        <v-btn size="x-small" color="primary" variant="text" prepend-icon="mdi-plus" @click="openExamDialog()">Add Exam</v-btn>
                    </div>
                    <v-divider class="mb-2"></v-divider>
                    <v-list density="compact" class="pa-0">
                        <v-list-item v-for="(exam, index) in offeringData.examinations" :key="index" border class="mb-1 rounded">
                            <v-list-item-title class="text-body-2">{{ exam.name }}</v-list-item-title>
                            <v-list-item-subtitle class="text-caption">{{ exam.max_marks }} Marks</v-list-item-subtitle>
                            <template v-slot:append>
                                <v-btn icon="mdi-pencil" size="x-small" variant="text" @click="openExamDialog(exam, index)"></v-btn>
                                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteExam(exam, index)"></v-btn>
                            </template>
                        </v-list-item>
                        <div v-if="!offeringData.examinations?.length" class="text-center py-2 text-caption text-medium-emphasis border rounded border-dashed">
                            No examinations added yet
                        </div>
                    </v-list>
                </div>

                <div class="mt-4">
                    <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-subtitle-2">Teachers</div>
                    </div>
                    <v-divider class="mb-2"></v-divider>
                    <v-row class="mb-2" dense>
                        <v-col cols="10">
                            <v-select
                                v-model="selectedTeacherId"
                                :items="allTeachers"
                                item-title="name"
                                item-value="id"
                                label="Assign Teacher"
                                variant="outlined"
                                density="compact"
                                hide-details
                            ></v-select>
                        </v-col>
                        <v-col cols="2">
                            <v-btn 
                                block 
                                color="primary" 
                                height="40" 
                                @click="addTeacherToOffering" 
                                :loading="addingTeacher"
                                :disabled="!selectedTeacherId"
                            >Add</v-btn>
                        </v-col>
                    </v-row>
                    <v-list density="compact" class="pa-0">
                        <v-list-item v-for="(teacher, index) in offeringData.teachers" :key="index" border class="mb-1 rounded">
                            <v-list-item-title class="text-body-2">{{ teacher.teacher_name }}</v-list-item-title>
                            <v-list-item-subtitle class="text-caption">{{ teacher.teacher_id }}</v-list-item-subtitle>
                            <template v-slot:append>
                                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="removeTeacherFromOffering(teacher, index)"></v-btn>
                            </template>
                        </v-list-item>
                        <div v-if="!offeringData.teachers?.length" class="text-center py-2 text-caption text-medium-emphasis border rounded border-dashed">
                            No teachers assigned yet
                        </div>
                    </v-list>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="offeringDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveOffering" :loading="savingOffering">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Exam Dialog -->
    <v-dialog v-model="examDialog" max-width="400">
        <v-card>
            <v-card-title>{{ editingExam ? 'Edit Examination' : 'Add Examination' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="examData.name"
                    label="Exam Name"
                    variant="outlined"
                    density="compact"
                    placeholder="e.g. Mid Term, End Sem"
                ></v-text-field>
                <v-text-field
                    v-model.number="examData.max_marks"
                    label="Max Marks"
                    type="number"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
                <v-text-field
                    v-model="examData.date"
                    label="Exam Date (Optional)"
                    type="date"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="examDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveExam" :loading="savingExam">Save Exam</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Bulk Upload Result Dialog -->
    <v-dialog v-model="resultDialog" max-width="600">
        <v-card>
            <v-card-title :class="['text-h6', resultStats.errors?.length ? 'text-warning' : 'text-success']">
                {{ resultStats.errors?.length ? 'Upload Completed with Errors' : 'Upload Successful' }}
            </v-card-title>
            <v-card-text>
                <div class="text-subtitle-1 mb-2">
                    Successfully Created: {{ resultStats.created }}
                </div>
                
                <div v-if="resultStats.errors?.length">
                    <div class="text-subtitle-2 text-error mb-1">Errors ({{ resultStats.errors.length }}):</div>
                    <v-sheet border class="pa-2 overflow-y-auto" max-height="300" color="grey-lighten-4">
                        <div v-for="(error, i) in resultStats.errors" :key="i" class="text-caption text-error mb-1">
                            {{ error }}
                        </div>
                    </v-sheet>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="resultDialog = false">Close</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color">
        {{ snackbar.text }}
    </v-snackbar>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'
import { downloadDataAsCSV } from '../../utils/csv'

const auth = useAuthStore()

// State
const semesters = ref([])
const courses = ref([])
const users = ref([])
const offerings = ref([])
const loadingOfferings = ref(false)
const selectedOfferingSemester = ref(null)
const searchOfferings = ref('')
const offeringDialog = ref(false)
const offeringData = ref({ course_code: '', semester_id: null, examinations: [], teachers: [] })
const editingOffering = ref(false)
const savingOffering = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })
const resultDialog = ref(false)
const resultStats = ref({ created: 0, errors: [] })

// Nested Exam State
const examDialog = ref(false)
const examData = ref({ name: '', max_marks: 100, date: null })
const editingExam = ref(false)
const savingExam = ref(false)
const currentExamIndex = ref(-1)

// Nested Teacher State
const addingTeacher = ref(false)
const selectedTeacherId = ref(null)

const allTeachers = computed(() => {
    return users.value.filter(u => u.roles.some(r => r.role === 'teacher'))
})

const offeringHeaders = [
    { title: 'Course Code', key: 'course_code' },
    { title: 'Course Name', key: 'course.name' },
    { title: 'Category', key: 'course.category' },
    { title: 'Examinations', key: 'examinations', sortable: false },
    { title: 'Teachers', key: 'teachers', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

const offeringFile = ref(null)
const uploadingOfferings = ref(false)

const fetchData = async () => {
    try {
        const [semRes, courseRes, userRes] = await Promise.all([
            axios.get('http://localhost:8000/api/v1/academic/semesters/', { headers: { Authorization: `Bearer ${auth.token}` } }),
            axios.get('http://localhost:8000/api/v1/courses/', { headers: { Authorization: `Bearer ${auth.token}` } }),
            axios.get('http://localhost:8000/api/v1/users/', { headers: { Authorization: `Bearer ${auth.token}` } })
        ])
        semesters.value = semRes.data
        courses.value = courseRes.data
        users.value = userRes.data
    } catch (e) { console.error(e) }
}

const fetchOfferings = async () => {
    if (!selectedOfferingSemester.value) {
        offerings.value = []
        return
    }
    loadingOfferings.value = true
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/courses/semester-courses?semester_id=${selectedOfferingSemester.value}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        offerings.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loadingOfferings.value = false
    }
}

const openOfferingDialog = (item = null) => {
    if (item) {
        offeringData.value = JSON.parse(JSON.stringify(item))
        editingOffering.value = true
    } else {
        offeringData.value = { course_code: '', semester_id: selectedOfferingSemester.value, examinations: [], teachers: [] }
        editingOffering.value = false
    }
    offeringDialog.value = true
}

const saveOffering = async () => {
    savingOffering.value = true
    try {
        let offeringId = offeringData.value.id
        if (editingOffering.value) {
            await axios.put(`http://localhost:8000/api/v1/courses/offerings/${offeringData.value.id}`, offeringData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            const res = await axios.post('http://localhost:8000/api/v1/courses/offerings/', offeringData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            offeringId = res.data.id
            for (const exam of offeringData.value.examinations) {
                await axios.post('http://localhost:8000/api/v1/examinations/', { ...exam, course_offering_id: offeringId }, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
            }
            for (const teacher of offeringData.value.teachers) {
                await axios.post(`http://localhost:8000/api/v1/courses/offerings/${offeringId}/teachers?teacher_id=${teacher.teacher_id}`, {}, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
            }
        }
        snackbar.value = { show: true, text: 'Offering saved successfully', color: 'success' }
        offeringDialog.value = false
        fetchOfferings()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save offering: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingOffering.value = false
    }
}

const deleteOffering = async (item) => {
    if (!confirm(`Are you sure you want to delete offering for ${item.course_code}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/courses/offerings/${item.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Offering deleted', color: 'success' }
        fetchOfferings()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to delete: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

// Exam methods
const openExamDialog = (item = null, index = -1) => {
    if (item) {
        examData.value = { ...item }
        editingExam.value = true
        currentExamIndex.value = index
    } else {
        examData.value = { name: '', max_marks: 100, date: null }
        editingExam.value = false
        currentExamIndex.value = -1
    }
    examDialog.value = true
}

const saveExam = async () => {
    if (editingOffering.value && examData.value.id) {
        savingExam.value = true
        try {
            await axios.put(`http://localhost:8000/api/v1/examinations/${examData.value.id}`, examData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            const idx = offeringData.value.examinations.findIndex(e => e.id === examData.value.id)
            if (idx !== -1) offeringData.value.examinations[idx] = { ...examData.value }
            examDialog.value = false
        } catch (e) {
             snackbar.value = { show: true, text: 'Failed to save exam: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingExam.value = false
        }
    } else if (editingOffering.value && !examData.value.id) {
        savingExam.value = true
        try {
            const res = await axios.post('http://localhost:8000/api/v1/examinations/', { 
                ...examData.value, 
                course_offering_id: offeringData.value.id 
            }, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            offeringData.value.examinations.push(res.data)
            examDialog.value = false
        } catch (e) {
             snackbar.value = { show: true, text: 'Failed to create exam: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingExam.value = false
        }
    } else {
        if (currentExamIndex.value !== -1) {
            offeringData.value.examinations[currentExamIndex.value] = { ...examData.value }
        } else {
            offeringData.value.examinations.push({ ...examData.value })
        }
        examDialog.value = false
    }
}

const deleteExam = async (item, index) => {
    if (!confirm(`Are you sure you want to delete exam ${item.name}?`)) return
    if (editingOffering.value && item.id) {
        try {
            await axios.delete(`http://localhost:8000/api/v1/examinations/${item.id}`, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            offeringData.value.examinations.splice(index, 1)
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to delete exam: ' + (e.response?.data?.detail || e.message), color: 'error' }
        }
    } else {
        offeringData.value.examinations.splice(index, 1)
    }
}

// Teacher methods
const addTeacherToOffering = async () => {
    if (!selectedTeacherId.value) return
    const teacher = allTeachers.value.find(u => u.id === selectedTeacherId.value)
    if (!teacher) return

    if (editingOffering.value) {
        addingTeacher.value = true
        try {
            const res = await axios.post(`http://localhost:8000/api/v1/courses/offerings/${offeringData.value.id}/teachers?teacher_id=${selectedTeacherId.value}`, {}, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            offeringData.value.teachers.push(res.data)
            selectedTeacherId.value = null
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to add teacher: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            addingTeacher.value = false
        }
    } else {
        if (!offeringData.value.teachers.some(t => t.teacher_id === teacher.id)) {
            offeringData.value.teachers.push({
                teacher_id: teacher.id,
                teacher_name: teacher.name
            })
        }
        selectedTeacherId.value = null
    }
}

const removeTeacherFromOffering = async (teacher, index) => {
    if (!confirm(`Are you sure you want to remove ${teacher.teacher_name}?`)) return
    if (editingOffering.value && teacher.id) {
        try {
            await axios.delete(`http://localhost:8000/api/v1/courses/offerings/${offeringData.value.id}/teachers/${teacher.teacher_id}`, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            offeringData.value.teachers.splice(index, 1)
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to remove teacher: ' + (e.response?.data?.detail || e.message), color: 'error' }
        }
    } else {
        offeringData.value.teachers.splice(index, 1)
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
        const errors = res.data.errors
        
        resultStats.value = { created: count, errors: errors }
        resultDialog.value = true

        offeringFile.value = null
        fetchOfferings()
    } catch (e) {
        snackbar.value = { show: true, text: 'Upload failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        uploadingOfferings.value = false
    }
}

const downloadOfferings = () => {
    downloadDataAsCSV(offerings.value, offeringHeaders, 'Course_Offerings', auth.user?.name || 'User')
}

onMounted(() => {
    fetchData()
})
</script>
