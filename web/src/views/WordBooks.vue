<template>
  <div class="page-container">
    <PageHeader title="选择单词书">
      <el-select v-model="category" placeholder="按类别筛选" clearable size="large"
        class="filter" @change="loadBooks">
        <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
      </el-select>
    </PageHeader>

    <div v-if="wordBook.books.length" class="books">
      <BookCard
        v-for="b in wordBook.books"
        :key="b.id"
        :book="b"
        :picked="pickedId === b.id"
        @select="select"
      />
    </div>
    <el-empty v-else description="暂无单词书" />

    <div class="actions">
      <el-button v-if="wordBook.current" type="primary" size="large" round @click="toLearning">
        🚀 继续学习「{{ wordBook.current.name }}」
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useWordBookStore } from '@/stores/wordBook'
import { useSettingsStore } from '@/stores/settings'
import { startLearning } from '@/api/learning'
import { useNavigate } from '@/router'

const wordBook = useWordBookStore()
const { toLearning } = useNavigate()
const category = ref('')
const pickedId = ref(null)

const categories = computed(() =>
  [...new Set(wordBook.books.map((b) => b.category).filter(Boolean))]
)

async function loadBooks() {
  const params = {}
  if (category.value) params.category = category.value
  await wordBook.fetchBooks(params)
  // 恢复之前选中的词书（跨页面跳转后 pickedId 仍正确）
  const settings = useSettingsStore()
  if (settings.currentBookId) {
    pickedId.value = settings.currentBookId
    wordBook.restoreCurrent(settings.currentBookId)
  }
}
async function select(book) {
  pickedId.value = book.id
  await wordBook.selectBook(book.id)
  await startLearning(book.id) // 初始化学习记录
}

loadBooks()
</script>

<style scoped>
.filter {
  width: 200px;
}
.books {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 18px;
}
.actions {
  text-align: center;
  margin-top: 24px;
}
</style>