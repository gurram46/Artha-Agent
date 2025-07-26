from setuptools import setup, find_packages

setup(
    name='smart-budget-agent',
    version='0.1.0',
    description='Smart Budget Agent for processing financial emails',
    author='Grandhi',
    author_email='yaswanthgrandhi2580@gmail.com',
    url='https://github.com/grandhi/smart-budget-agent',
    packages=find_packages(),
    install_requires=[
        'firebase-admin==6.2.0',
        'python-dotenv>=1.1.1,<2.0.0',
        'google-auth-oauthlib>=1.2.2,<2.0.0',
        'google-api-python-client>=2.176.0,<3.0.0',
        'google-auth-httplib2>=0.2.0,<0.3.0',
        'google-cloud-aiplatform==1.38.1',
        'google-cloud-storage>=1.32.0,<3.0.0',
        'pandas',
        'numpy',
        'scikit-learn'
    ],
    python_requires='>=3.12,<4.0'
)
