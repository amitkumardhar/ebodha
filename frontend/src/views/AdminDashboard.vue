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

                <v-text-field
                    v-model="searchUsers"
                    prepend-inner-icon="mdi-magnify"
                    label="Search Users"
                    variant="outlined"
                    density="compact"
                    hide-details
                    class="mb-4"
                    clearable
                ></v-text-field>

                <v-data-table
                    :headers="userHeaders"
                    :items="users"
                    :loading="loadingUsers"
                    :search="searchUsers"
                    density="compact"
                    class="mb-6"
                >
                    <template v-slot:item.roles="{ item }">
                        <v-chip
                            v-for="roleEntry in item.roles"
                            :key="roleEntry.role"
                            size="x-small"
                            class="mr-1 text-uppercase"
                            color="secondary"
                            variant="tonal"
                        >
                            {{ roleEntry.role }}
                        </v-chip>
                    </template>
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
                    <template v-slot:item.calendar_events="{ item }">
                        <div v-for="event in item.calendar_events" :key="event.id" class="text-caption">
                            {{ event.name }} ({{ event.start_date }} - {{ event.end_date }})
                        </div>
                        <span v-if="!item.calendar_events?.length" class="text-caption text-medium-emphasis">No events</span>
                    </template>
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

                <v-text-field
                    v-model="searchCourses"
                    prepend-inner-icon="mdi-magnify"
                    label="Search Courses"
                    variant="outlined"
                    density="compact"
                    hide-details
                    class="mb-4"
                    clearable
                ></v-text-field>
                
                <v-data-table
                    :headers="courseHeaders"
                    :items="courses"
                    :loading="loadingCourses"
                    :search="searchCourses"
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
                    v-model="userData.roles"
                    :items="['student', 'teacher', 'administrator', 'alumni']"
                    label="Roles"
                    variant="outlined"
                    multiple
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
                <v-row>
                    <v-col cols="6">
                        <v-text-field
                            v-if="!editingSemester"
                            v-model.number="semesterData.id"
                            label="Semester ID"
                            type="number"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.name"
                            label="Semester Name"
                            variant="outlined"
                            density="compact"
                            placeholder="e.g. Autumn 2025"
                        ></v-text-field>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.start_date"
                            label="Start Date"
                            type="date"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.end_date"
                            label="End Date"
                            type="date"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                </v-row>
                <v-switch
                    v-model="semesterData.is_active"
                    label="Current Semester"
                    color="primary"
                    density="compact"
                ></v-switch>

                <div class="mt-4">
                    <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-subtitle-2">Academic Events</div>
                        <v-btn size="x-small" color="primary" variant="text" prepend-icon="mdi-plus" @click="openEventDialog()">Add Event</v-btn>
                    </div>
                    <v-divider class="mb-2"></v-divider>
                    <v-list density="compact" class="pa-0">
                        <v-list-item v-for="(event, index) in semesterData.calendar_events" :key="index" border class="mb-1 rounded">
                            <v-list-item-title class="text-body-2">{{ event.name }}</v-list-item-title>
                            <v-list-item-subtitle class="text-caption">{{ event.start_date }} to {{ event.end_date }}</v-list-item-subtitle>
                            <template v-slot:append>
                                <v-btn icon="mdi-pencil" size="x-small" variant="text" @click="openEventDialog(event, index)"></v-btn>
                                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteEvent(event, index)"></v-btn>
                            </template>
                        </v-list-item>
                        <div v-if="!semesterData.calendar_events?.length" class="text-center py-2 text-caption text-medium-emphasis border rounded border-dashed">
                            No academic events added yet
                        </div>
                    </v-list>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="semesterDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveSemester" :loading="savingSemester">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

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

    <!-- Event Dialog -->
    <v-dialog v-model="eventDialog" max-width="400">
        <v-card>
            <v-card-title>{{ editingEvent ? 'Edit Event' : 'Add Academic Event' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="eventData.name"
                    label="Event Name"
                    variant="outlined"
                    density="compact"
                    placeholder="e.g. Registration, Mid-Sem Break"
                ></v-text-field>
                <v-text-field
                    v-model="eventData.start_date"
                    label="Start Date"
                    type="date"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
                <v-text-field
                    v-model="eventData.end_date"
                    label="End Date"
                    type="date"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="eventDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveEvent" :loading="savingEvent">Save Event</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

     <v-snackbar v-model="snackbar.show" :color="snackbar.color">
        {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const tab = ref('users')

// Semesters
const semesters = ref([])
const loadingSemesters = ref(false)
const semesterDialog = ref(false)
const semesterData = ref({ id: null, name: '', start_date: '', end_date: '', is_active: false, calendar_events: [] })
const editingSemester = ref(false)
const savingSemester = ref(false)

const semesterHeaders = [
    { title: 'Semester ID', key: 'id' },
    { title: 'Name', key: 'name' },
    { title: 'Start Date', key: 'start_date' },
    { title: 'End Date', key: 'end_date' },
    { title: 'Events', key: 'calendar_events', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

// Academic Events Management (Nested)
const eventDialog = ref(false)
const eventData = ref({ name: '', start_date: '', end_date: '' })
const editingEvent = ref(false)
const savingEvent = ref(false)
const currentEventIndex = ref(-1)

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
        semesterData.value = JSON.parse(JSON.stringify(item))
        editingSemester.value = true
    } else {
        semesterData.value = { id: null, name: '', start_date: '', end_date: '', is_active: false, calendar_events: [] }
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
            const res = await axios.post('http://localhost:8000/api/v1/academic/semesters/', semesterData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            const semesterId = res.data.id
            // If new semester, create pending events
            for (const event of semesterData.value.calendar_events) {
                await axios.post('http://localhost:8000/api/v1/academic/events/', { ...event, semester_id: semesterId }, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
            }
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

const openEventDialog = (item = null, index = -1) => {
    if (item) {
        eventData.value = { ...item }
        editingEvent.value = true
        currentEventIndex.value = index
    } else {
        eventData.value = { name: '', start_date: '', end_date: '' }
        editingEvent.value = false
        currentEventIndex.value = -1
    }
    eventDialog.value = true
}

const saveEvent = async () => {
    if (editingSemester.value && eventData.value.id) {
        savingEvent.value = true
        try {
            await axios.put(`http://localhost:8000/api/v1/academic/events/${eventData.value.id}`, eventData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            const idx = semesterData.value.calendar_events.findIndex(e => e.id === eventData.value.id)
            if (idx !== -1) semesterData.value.calendar_events[idx] = { ...eventData.value }
            eventDialog.value = false
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to save event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingEvent.value = false
        }
    } else if (editingSemester.value && !eventData.value.id) {
        savingEvent.value = true
        try {
            const res = await axios.post('http://localhost:8000/api/v1/academic/events/', {
                ...eventData.value,
                semester_id: semesterData.value.id
            }, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            semesterData.value.calendar_events.push(res.data)
            eventDialog.value = false
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to create event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingEvent.value = false
        }
    } else {
        if (currentEventIndex.value !== -1) {
            semesterData.value.calendar_events[currentEventIndex.value] = { ...eventData.value }
        } else {
            semesterData.value.calendar_events.push({ ...eventData.value })
        }
        eventDialog.value = false
    }
}

const deleteEvent = async (item, index) => {
    if (!confirm(`Are you sure you want to delete event ${item.name}?`)) return
    if (editingSemester.value && item.id) {
        try {
            await axios.delete(`http://localhost:8000/api/v1/academic/events/${item.id}`, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            semesterData.value.calendar_events.splice(index, 1)
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to delete event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        }
    } else {
        semesterData.value.calendar_events.splice(index, 1)
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
    { title: 'Roles', key: 'roles', sortable: false },
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
        userData.value = { 
            ...item,
            roles: item.roles ? item.roles.map(r => r.role) : []
        }
        editingUser.value = true
    } else {
        userData.value = { id: '', name: '', email: '', password: '', roles: ['student'], discipline_code: null, is_active: true }
        editingUser.value = false
    }
    userDialog.value = true
}

const saveUser = async () => {
    savingUser.value = true
    try {
        // Prepare data
        const data = { ...userData.value }
        
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

const searchUsers = ref('')
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

const searchCourses = ref('')

// Offerings Management
const offerings = ref([])
const loadingOfferings = ref(false)
const selectedOfferingSemester = ref(null)
const searchOfferings = ref('')
const offeringDialog = ref(false)
const offeringData = ref({ course_code: '', semester_id: null })
const editingOffering = ref(false)
const savingOffering = ref(false)

const offeringHeaders = [
    { title: 'Course Code', key: 'course_code' },
    { title: 'Course Name', key: 'course.name' },
    { title: 'Category', key: 'course.category' },
    { title: 'Examinations', key: 'examinations', sortable: false },
    { title: 'Teachers', key: 'teachers', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

// Examinations Management (Nested)
const examDialog = ref(false)
const examData = ref({ name: '', max_marks: 100, date: null })
const editingExam = ref(false)
const savingExam = ref(false)
const currentExamIndex = ref(-1)

// Teachers Management (Nested)
const addingTeacher = ref(false)
const selectedTeacherId = ref(null)

const allTeachers = computed(() => {
    return users.value.filter(u => u.roles.some(r => r.role === 'teacher'))
})

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
    } catch(e) { console.error(e) }
    finally { loadingOfferings.value = false }
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
            
            // Create pending exams for new offering
            for (const exam of offeringData.value.examinations) {
                await axios.post('http://localhost:8000/api/v1/examinations/', { ...exam, course_offering_id: offeringId }, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
            }
            
            // Create pending teacher assignments for new offering
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
        // Update existing exam in DB
        savingExam.value = true
        try {
            await axios.put(`http://localhost:8000/api/v1/examinations/${examData.value.id}`, examData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            // Update local state
            const idx = offeringData.value.examinations.findIndex(e => e.id === examData.value.id)
            if (idx !== -1) offeringData.value.examinations[idx] = { ...examData.value }
            examDialog.value = false
        } catch (e) {
             snackbar.value = { show: true, text: 'Failed to save exam: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingExam.value = false
        }
    } else if (editingOffering.value && !examData.value.id) {
        // Create new exam for existing offering
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
        // Create/Update in local list for new offering
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
        // Just add to local list for new offering
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
