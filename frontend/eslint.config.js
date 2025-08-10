import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { 
    ignores: ['dist', 'build', 'node_modules', '*.config.js'] 
  },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2025,
      globals: {
        ...globals.browser,
        ...globals.es2025,
        process: 'readonly'
      },
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    settings: { 
      react: { version: '19.0' }
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      
      // React 19 specific optimizations
      'react/jsx-no-target-blank': 'off',
      'react/prop-types': 'off', // Using TypeScript for type checking
      'react/react-in-jsx-scope': 'off', // React 19 auto-import
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      
      // Performance optimizations
      'no-unused-vars': ['error', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_' 
      }],
      'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      
      // Modern JS optimizations
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-arrow-callback': 'error'
    },
  },
]