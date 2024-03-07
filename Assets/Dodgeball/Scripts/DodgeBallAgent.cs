using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using MLAgents;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Policies;
using UnityEngine.Windows;
using Random = UnityEngine.Random;

public class DodgeBallAgent : Agent
{
    [Header("TEAM")]
    public int teamID;
    private AgentCubeMovement m_CubeMovement;
    public ThrowBall ThrowController;

    [Header("HEALTH")] public AgentHealth AgentHealth;
    public int NumberOfTimesPlayerCanBeHit = 5;
    public int HitPointsRemaining; //how many more times can we be hit
    public HeadBand headBand;

    [Header("SHIELD")] public ShieldController AgentShield;

    [Header("INPUT")]
    public DodgeBallAgentInput input;

    [Header("INVENTORY")]
    public int currentNumberOfBalls;
    public List<DodgeBall> currentlyHeldBalls;

    [Header("WAYPOINTS")]
    [SerializeField]
    private Transform waypointsContainer;
    private List<Transform> waypoints;
    // private int currentWaypointIndex = 0;
    // private float waypointReachDistance = 7f;
    private float agentSpeed = 5f;

    [Header("SENSORS")]
    public RayPerceptionSensorComponent3D AgentRaycastSensor;
    public RayPerceptionSensorComponent3D BackRaycastSensor;
    public RayPerceptionSensorComponent3D BallRaycastSensor;
    public RayPerceptionSensorComponent3D WallRaycastSensor;

    public bool UseVectorObs;
    public Transform HomeBaseLocation;
    public Transform TeamFlag;
    private DodgeBallGameController m_GameController;

    private Vector3 m_StartingPos;
    private Quaternion m_StartingRot;
    [HideInInspector]
    public Rigidbody AgentRb;

    [Header("HIT EFFECTS")] public ParticleSystem HitByParticles;
    private AudioSource m_BallImpactAudioSource;
    private AudioSource m_StunnedAudioSource;
    public Queue<DodgeBall> ActiveBallsQueue = new Queue<DodgeBall>();
    public List<Transform> BallUIList = new List<Transform>();

    public bool AnimateEyes;
    public Transform NormalEyes;
    public Transform HitEyes;
    public Transform StunnedEyes;
    public ParticleSystem StunnedEffect;
    public Transform Flag;
    public Transform StunnedCollider;

    [Header("ANIMATIONS")] public Animator FlagAnimator;
    public Animator VictoryDanceAnimation;

    [Header("Gamelog")]
    public GameLogger m_gameLogger;

    [Header("OTHER")] public bool m_PlayerInitialized;
    public BehaviorParameters m_BehaviorParameters;
    public bool useRuleBasedAgent = false;
    public bool useStillAgent = false;

    public float m_InputH;
    private Vector3 m_HomeBasePosition;
    private Vector3 m_HomeDirection;
    private float m_InputV;
    private float m_Rotate;
    public float rotationSpeed = 5f;
    public float m_ThrowInput;
    public float m_DashInput;
    private bool m_FirstInitialize = true;
    private bool m_DashCoolDownReady;
    private bool m_IsStunned;
    public float m_StunTime;
    private float m_OpponentHasFlagPenalty;
    private float m_TeamHasFlagBonus;
    private float m_BallHoldBonus = 0.0f;
    private float m_LocationNormalizationFactor = 80.0f; // About the size of a reasonable stage
    private EnvironmentParameters m_EnvParameters;

    public BufferSensorComponent m_BallBuffer;
    public BufferSensorComponent m_OtherAgentsBuffer;
    float[] ballOneHot = new float[5];

    // Eye tracking variables
    private GameObject thisObject;  // Agent object for eye tracking
    private int haveStarted = 0;
    public Rect myCurrentObjectRect;
    public Rect myPreviousObjectRect;
    public int previousUpdateTime;
    public int currentUpdateTime;
    public string ttW;
    public Boolean eyeTrackingActive = true;
    public Vector2 direction { get; private set; }

    //is the current step a decision step for the agent
    private bool m_IsDecisionStep;

    // variables for the rule based agent (FSM)
    private float previousMovementAngle;
    public int fsm_version;

    [HideInInspector]
    //because heuristic only runs every 5 fixed update steps, the input for a human feels really bad
    //set this to true on an agent that you want to be human playable and it will collect input every
    //FixedUpdate tick instead of ever decision step
    public bool disableInputCollectionInHeuristicCallback;

    public override void Initialize()
    {
        //Disable logging
        Debug.unityLogger.logEnabled = true;

        thisObject = GameObject.FindObjectsOfType<GameObject>().Where(obj => obj.name == "AgentCube")
            .Where(obj => obj.tag == "purpleAgent").ToArray()[0];

        //SETUP STUNNED AS
        m_StunnedAudioSource = gameObject.AddComponent<AudioSource>();
        m_StunnedAudioSource.spatialBlend = 1;
        m_StunnedAudioSource.maxDistance = 250;


        //SETUP IMPACT AS
        m_BallImpactAudioSource = gameObject.AddComponent<AudioSource>();
        m_BallImpactAudioSource.spatialBlend = 1;
        m_BallImpactAudioSource.maxDistance = 250;

        var bufferSensors = GetComponentsInChildren<BufferSensorComponent>();
        m_OtherAgentsBuffer = bufferSensors[0];
        m_CubeMovement = GetComponent<AgentCubeMovement>();
        m_BehaviorParameters = gameObject.GetComponent<BehaviorParameters>();


        AgentRb = GetComponent<Rigidbody>();
        input = GetComponent<DodgeBallAgentInput>();
        m_GameController = GetComponentInParent<DodgeBallGameController>();

        m_gameLogger = GetComponent<GameLogger>();

        //Make sure ThrowController is set up to play sounds
        ThrowController.PlaySound = m_GameController.ShouldPlayEffects;

        if (m_FirstInitialize)
        {
            m_StartingPos = transform.position;
            m_StartingRot = transform.rotation;

            if (useRuleBasedAgent)
            {

                AgentRaycastSensor = transform.Find("AgentRaycastSensor").GetComponent<RayPerceptionSensorComponent3D>();
                BackRaycastSensor = transform.Find("BackRaycastSensor").GetComponent<RayPerceptionSensorComponent3D>();
                BallRaycastSensor = transform.Find("BallRaycastSensor").GetComponent<RayPerceptionSensorComponent3D>();
                WallRaycastSensor = transform.Find("WallRaycastSensor").GetComponent<RayPerceptionSensorComponent3D>();

                previousMovementAngle = 90; // 90 as in straight forward
            }

            //If we don't have a home base, just use the starting position.
            if (HomeBaseLocation is null)
            {
                m_HomeBasePosition = m_StartingPos;
                m_HomeDirection = transform.forward;
            }
            else
            {
                m_HomeBasePosition = HomeBaseLocation.position;
                m_HomeDirection = HomeBaseLocation.forward;
            }
            m_FirstInitialize = false;
            Flag.gameObject.SetActive(false);
        }
        m_EnvParameters = Academy.Instance.EnvironmentParameters;
        GetAllParameters();
    }

    //Get all environment parameters for agent
    private void GetAllParameters()
    {
        m_StunTime = m_EnvParameters.GetWithDefault("stun_time", 10.0f);
        m_OpponentHasFlagPenalty = m_EnvParameters.GetWithDefault("opponent_has_flag_penalty", 0f);
        m_TeamHasFlagBonus = m_EnvParameters.GetWithDefault("team_has_flag_bonus", 0f);
        m_BallHoldBonus = m_EnvParameters.GetWithDefault("ball_hold_bonus", 0f);
    }

    public void ResetAgent()
    {
        GetAllParameters();
        StopAllCoroutines();
        transform.position = m_StartingPos;
        AgentRb.constraints = RigidbodyConstraints.FreezeRotation;
        if (m_GameController.CurrentSceneType == DodgeBallGameController.SceneType.Game || m_GameController.CurrentSceneType == DodgeBallGameController.SceneType.Movie)
        {
            transform.rotation = m_StartingRot;
        }
        else //Training Mode so we want random rotations
        {
            transform.rotation = Quaternion.Euler(new Vector3(0f, Random.Range(0, 360)));
        }
        ActiveBallsQueue.Clear();
        currentNumberOfBalls = 0;
        AgentRb.velocity = Vector3.zero;
        AgentRb.angularVelocity = Vector3.zero;
        SetActiveBalls(0);
        NormalEyes.gameObject.SetActive(true);
        HitEyes.gameObject.SetActive(false);
        HasEnemyFlag = false;
        Stunned = false;
        AgentRb.drag = 4;
        AgentRb.angularDrag = 1;
        Dancing = false;
    }

    //Set agent to stunned, then send it back to spawn point.
    public void StunAndReset()
    {
        DropAllBalls();
        StartCoroutine(StunThenReset());
    }

    IEnumerator StunThenReset()
    {
        WaitForFixedUpdate wait = new WaitForFixedUpdate();
        float timer = 0;
        Stunned = true;
        while (timer < m_StunTime)
        {
            timer += Time.fixedDeltaTime;
            yield return wait;
        }
        //Play poof as agent gets removed from level
        if (m_GameController.usePoofParticlesOnElimination)
        {
            m_GameController.PlayParticleAtPosition(transform.position);
        }
        ResetAgent();
        //Play second poof as agent respawns
        if (m_GameController.usePoofParticlesOnElimination)
        {
            m_GameController.PlayParticleAtPosition(transform.position);
        }
    }

    //Set the number of active balls.
    void SetActiveBalls(int numOfBalls)
    {
        int i = 0;
        foreach (var item in BallUIList)
        {
            var active = i < numOfBalls;
            BallUIList[i].gameObject.SetActive(active);
            i++;
        }
    }

    public void SetHeadBandColor(int hp)
    {
        // Resources.Load<Material>("pink");
        switch (hp)  // Headband should change color when hit
        {
            case 3:
                headBand.setGreenBand();
                break;
            case 2:
                headBand.setYellowBand();
                break;
            case 1:
                headBand.setRedBand();
                break;
        }
    }

    private int m_AgentStepCount; //current agent step
    void FixedUpdate()
    {
        m_DashCoolDownReady = m_CubeMovement.dashCoolDownTimer > m_CubeMovement.dashCoolDownDuration;
        if (StepCount % 5 == 0)
        {
            m_IsDecisionStep = true;
            m_AgentStepCount++;
        }
        // Handle if flag gets home
        if (Vector3.Distance(m_HomeBasePosition, transform.position) <= 3.0f && HasEnemyFlag)
        {
            m_GameController.FlagWasBroughtHome(this);
        }
    }

    //Collect observations, to be used by the agent in ML-Agents.
    public override void CollectObservations(VectorSensor sensor)
    {
        AddReward(m_BallHoldBonus * (float)currentNumberOfBalls);

        if (true) // This seems to be set to false at times
        {
            sensor.AddObservation(ThrowController.coolDownWait); //Held DBs Normalized
            sensor.AddObservation(Stunned);
            Array.Clear(ballOneHot, 0, 5);
            ballOneHot[currentNumberOfBalls] = 1f;
            sensor.AddObservation(ballOneHot); //Held DBs Normalized
            sensor.AddObservation((float)HitPointsRemaining / (float)NumberOfTimesPlayerCanBeHit); //Remaining Hit Points Normalized

            sensor.AddObservation(Vector3.Dot(AgentRb.velocity, AgentRb.transform.forward));
            sensor.AddObservation(Vector3.Dot(AgentRb.velocity, AgentRb.transform.right));
            sensor.AddObservation(transform.InverseTransformDirection(m_HomeDirection));
            sensor.AddObservation(m_DashCoolDownReady);  // Remaining cooldown, capped at 1
            // Location to base
            sensor.AddObservation(GetRelativeCoordinates(m_HomeBasePosition));
            sensor.AddObservation(HasEnemyFlag);
        }

        //sensor.AddObservation(0);
        //sensor.AddObservation(0);
        //sensor.AddObservation(0);

        // FOLLOWING CODE IS SPECIFIC TO CAPTURE THE FLAG AND MORE THAN 1V1

        List<DodgeBallGameController.PlayerInfo> teamList;
        List<DodgeBallGameController.PlayerInfo> opponentsList;
        if (m_BehaviorParameters.TeamId == 0)
        {
            teamList = m_GameController.Team0Players;
            opponentsList = m_GameController.Team1Players;
        }
        else
        {
            teamList = m_GameController.Team1Players;
            opponentsList = m_GameController.Team0Players;
        }

        foreach (var info in teamList)
        {
            if (info.Agent != this && info.Agent.gameObject.activeInHierarchy)
            {
                m_OtherAgentsBuffer.AppendObservation(GetOtherAgentData(info));
            }
            if (info.Agent.HasEnemyFlag) // If anyone on my team has the enemy flag
            {
                AddReward(m_TeamHasFlagBonus);
            }
        }
        //Only opponents who picked up the flag are visible
        var currentFlagPosition = TeamFlag.transform.position;
        int numEnemiesRemaining = 0;
        bool enemyHasFlag = false;
        foreach (var info in opponentsList)
        {
            if (info.Agent.gameObject.activeInHierarchy)
            {
                numEnemiesRemaining++;
            }
            if (info.Agent.HasEnemyFlag)
            {
                enemyHasFlag = true;
                currentFlagPosition = info.Agent.transform.position;
                AddReward(m_OpponentHasFlagPenalty); // If anyone on the opposing team has a flag
            }
        }

        var portionOfEnemiesRemaining = (float)numEnemiesRemaining / (float)opponentsList.Count;


        //Different observation for different mode. Enemy Has Flag is only relevant to CTF
        if (m_GameController.GameMode == DodgeBallGameController.GameModeType.CaptureTheFlag)
        {
            sensor.AddObservation(enemyHasFlag);
        }
        else
        {
            sensor.AddObservation(numEnemiesRemaining);
        }


        //Location to flag
        sensor.AddObservation(GetRelativeCoordinates(currentFlagPosition));

    }

    //Get normalized position relative to agent's current position.
    private float[] GetRelativeCoordinates(Vector3 pos)
    {
        Vector3 relativeHome = transform.InverseTransformPoint(pos);
        var relativeCoordinate = new float[2];
        relativeCoordinate[0] = (relativeHome.x) / m_LocationNormalizationFactor;
        relativeCoordinate[1] = (relativeHome.z) / m_LocationNormalizationFactor;
        return relativeCoordinate;
    }

    //Get information of teammate
    private float[] GetOtherAgentData(DodgeBallGameController.PlayerInfo info)
    {
        var otherAgentdata = new float[8];
        otherAgentdata[0] = (float)info.Agent.HitPointsRemaining / (float)NumberOfTimesPlayerCanBeHit;
        var relativePosition = transform.InverseTransformPoint(info.Agent.transform.position);
        otherAgentdata[1] = relativePosition.x / m_LocationNormalizationFactor;
        otherAgentdata[2] = relativePosition.z / m_LocationNormalizationFactor;
        otherAgentdata[3] = info.TeamID == teamID ? 0.0f : 1.0f;
        otherAgentdata[4] = info.Agent.HasEnemyFlag ? 1.0f : 0.0f;
        otherAgentdata[5] = info.Agent.Stunned ? 1.0f : 0.0f;
        var relativeVelocity = transform.InverseTransformDirection(info.Agent.AgentRb.velocity);
        otherAgentdata[6] = relativeVelocity.x / 30.0f;
        otherAgentdata[7] = relativeVelocity.z / 30.0f;
        return otherAgentdata;

    }

    //Excute agent movement
    public void MoveAgent(ActionBuffers actionBuffers)
    {
        if (Stunned)
        {
            return;
        }
        var continuousActions = actionBuffers.ContinuousActions;
        var discreteActions = actionBuffers.DiscreteActions;

        m_InputV = continuousActions[0];
        m_InputH = continuousActions[1];
        m_Rotate = continuousActions[2];

        if (teamID == 1)    // Rotation capping/smoothing only affecting purple team during training (our AI)
        {
            // Clamp and smooth rotation
            float maxRotationSpeed = 0.3f; // Change this value to adjust the maximum rotation speed
            m_Rotate = Mathf.Clamp(m_Rotate, -maxRotationSpeed, maxRotationSpeed);

            float targetRotation = transform.eulerAngles.y + m_Rotate;
            float rotationSpeed = 0.3f; // Change this value to adjust the smoothness of the rotation
            float smoothRotation = Mathf.LerpAngle(transform.eulerAngles.y, targetRotation, Time.fixedDeltaTime * rotationSpeed);
            transform.eulerAngles = new Vector3(transform.eulerAngles.x, smoothRotation, transform.eulerAngles.z);
        }

        m_ThrowInput = (int)discreteActions[0];
        m_DashInput = (int)discreteActions[1];

        //HANDLE ROTATION
        m_CubeMovement.Look(m_Rotate);
        // m_CubeMovement.LookZX();
        m_CubeMovement.LookT();

        //HANDLE XZ MOVEMENT
        var moveDir = transform.TransformDirection(new Vector3(m_InputH, 0, m_InputV));
        m_CubeMovement.RunOnGround(moveDir);

        //perform discrete actions only once between decisions
        if (m_IsDecisionStep)
        {
            m_IsDecisionStep = false;
            //HANDLE THROWING
            if (m_ThrowInput > 0)
            {
                ThrowTheBall();
            }
            //HANDLE DASH MOVEMENT
            if (m_DashInput > 0 && m_DashCoolDownReady)
            {
                m_CubeMovement.Dash(moveDir);
            }
        }
    }

    public void ThrowTheBall()
    {
        if (currentNumberOfBalls > 0 && !ThrowController.coolDownWait)
        {
            var db = ActiveBallsQueue.Peek();
            ThrowController.Throw(db, this, m_BehaviorParameters.TeamId);
            ActiveBallsQueue.Dequeue();
            currentNumberOfBalls--;
            SetActiveBalls(currentNumberOfBalls);

            //Log data
            if (m_BehaviorParameters.TeamId == 0)
            {
                m_gameLogger.blueBalls = currentNumberOfBalls;
                m_gameLogger.LogPlayerData(1); //Log player throw
            }
            else if (m_BehaviorParameters.TeamId == 1)
            {
                m_gameLogger.LogPlayerData(5); //Log enemy throw
            }
        }
    }

    public void DropAllBalls()
    {
        while (currentNumberOfBalls > 0)
        {
            var db = ActiveBallsQueue.Peek();
            ThrowController.Drop(db);
            ActiveBallsQueue.Dequeue();
            currentNumberOfBalls--;
            SetActiveBalls(currentNumberOfBalls);
        }
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        MoveAgent(actionBuffers);
    }

    IEnumerator ShowHitFace()
    {
        WaitForFixedUpdate wait = new WaitForFixedUpdate();
        float timer = 0;
        NormalEyes.gameObject.SetActive(false);
        HitEyes.gameObject.SetActive(true);
        while (timer < .25f)
        {
            timer += Time.deltaTime;
            yield return wait;
        }
        // Don't reshow face if this hit resulted in a stun
        if (!Stunned)
        {
            NormalEyes.gameObject.SetActive(true);
            HitEyes.gameObject.SetActive(false);
        }
    }

    public void PlayHitFX()
    {
        // Only shake if player object
        if (ThrowController.UseScreenShake && m_GameController.PlayerGameObject == gameObject)
        {
            ThrowController.impulseSource.GenerateImpulse();
        }
        PlayBallThwackSound();
        HitByParticles.Play();
        if (AnimateEyes)
        {
            StartCoroutine(ShowHitFace());
        }
    }

    public void PlayBallThwackSound()
    {
        if (m_GameController.ShouldPlayEffects)
        {
            m_BallImpactAudioSource.pitch = Random.Range(2f, 3f);
            m_BallImpactAudioSource.PlayOneShot(m_GameController.BallImpactClip2, 1f);
            m_BallImpactAudioSource.PlayOneShot(m_GameController.BallImpactClip1, 1f);
        }
    }

    public void PlayStunnedVoice()
    {
        if (m_GameController.ShouldPlayEffects)
        {
            m_StunnedAudioSource.pitch = Random.Range(.3f, .8f);
            m_StunnedAudioSource.PlayOneShot(m_GameController.HurtVoiceAudioClip, 1f);
        }
    }

    void ResetHeldFlag()
    {
        // Reset flag rotation
        Transform mesh = Flag.gameObject.transform.GetChild(0);
        mesh.localRotation = Quaternion.identity;
    }

    public bool HasEnemyFlag
    {
        get => Flag.gameObject.activeSelf;
        set
        {
            if (value)
            {
                Flag.gameObject.SetActive(true);
                ResetHeldFlag();
            }
            else
            {
                ResetHeldFlag();
                Flag.gameObject.SetActive(false);
            }
        }
    }

    public bool Stunned
    {
        get => m_IsStunned;
        set
        {
            if (value)
            {
                NormalEyes.gameObject.SetActive(false);
                HitEyes.gameObject.SetActive(false);
                StunnedEyes.gameObject.SetActive(true);
                StunnedEffect.Play();
                StunnedCollider.gameObject.SetActive(true);
                if (m_GameController.GameMode == DodgeBallGameController.GameModeType.CaptureTheFlag)
                {
                    AgentRb.mass = 100000;
                }
            }
            else
            {
                NormalEyes.gameObject.SetActive(true);
                HitEyes.gameObject.SetActive(false);
                StunnedEyes.gameObject.SetActive(false);
                StunnedEffect.Stop();
                StunnedCollider.gameObject.SetActive(false);
                AgentRb.mass = 10;
            }
            m_IsStunned = value;
        }
    }

    public bool Dancing
    {
        set
        {
            if (value)
            {
                VictoryDanceAnimation.enabled = true;
                m_IsStunned = true;
                Flag.gameObject.SetActive(false);
            }
            else
            {
                VictoryDanceAnimation.enabled = false;
                m_IsStunned = false;
                Flag.gameObject.SetActive(HasEnemyFlag);
            }
        }
    }

    private void OnCollisionEnter(Collision col)
    {
        // Ignore all collisions when stunned
        if (Stunned)
        {
            return;
        }
        DodgeBall db = col.gameObject.GetComponent<DodgeBall>();
        if (!db)
        {
            if (m_GameController.GameMode == DodgeBallGameController.GameModeType.CaptureTheFlag)
            {
                // Check if it is a flag
                if (col.gameObject.tag == "purpleFlag" && teamID == 0 || col.gameObject.tag == "blueFlag" && teamID == 1)
                {
                    m_GameController.FlagWasTaken(this);
                }
                else if (col.gameObject.tag == "purpleFlag" && teamID == 1 || col.gameObject.tag == "blueFlag" && teamID == 0)
                {
                    m_GameController.ReturnFlag(this);
                }
                DodgeBallAgent hitAgent = col.gameObject.GetComponent<DodgeBallAgent>();
                if (hitAgent && HasEnemyFlag && m_GameController.FlagCarrierKnockback)
                {
                    if (hitAgent.teamID != teamID && !hitAgent.Stunned)
                    {
                        if (m_GameController.ShouldPlayEffects)
                        {
                            m_BallImpactAudioSource.PlayOneShot(m_GameController.FlagHitClip, 1f);
                        }
                        // Play Flag Whack
                        if (FlagAnimator != null)
                        {
                            FlagAnimator.SetTrigger("FlagSwing");
                        }
                        hitAgent.PlayHitFX();
                        var moveDirection = hitAgent.transform.position - transform.position;
                        hitAgent.AgentRb.AddForce(moveDirection * 150, ForceMode.Impulse);
                    }
                }
            }
            return;
        }

        if (db.inPlay) //HIT BY LIVE BALL
        {
            if (db.TeamToIgnore != -1 && db.TeamToIgnore != m_BehaviorParameters.TeamId) //HIT BY LIVE BALL
            {
                PlayHitFX();
                // setActiveHealth();
                m_GameController.PlayerWasHit(this, db.thrownBy);
                db.BallIsInPlay(false);
            }
        }
        else //TRY TO PICK IT UP
        {
            if (currentNumberOfBalls < 4)
            {
                PickUpBall(db);
            }
        }
    }

    void PickUpBall(DodgeBall db)
    {
        if (m_GameController.ShouldPlayEffects)
        {
            m_BallImpactAudioSource.PlayOneShot(m_GameController.BallPickupClip, .1f);
        }

        //update counter
        currentNumberOfBalls++;
        SetActiveBalls(currentNumberOfBalls);

        //add to our inventory
        ActiveBallsQueue.Enqueue(db);
        db.BallIsInPlay(true);
        db.gameObject.SetActive(false);

        //Log data
        if (m_BehaviorParameters.TeamId == 0)
        {
            m_gameLogger.blueBalls = currentNumberOfBalls;
            m_gameLogger.LogPlayerData(2); // PlayerPickedUpBall
        }
        else
        {
            m_gameLogger.LogPlayerData(9); // EnemyPickedUpBall
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // if (disableInputCollectionInHeuristicCallback || m_IsStunned)
        // {
        //     return;
        // }

        //Use rule-based agent if enabled
        if (useRuleBasedAgent)
        {
            RuleBasedHeuristic(actionsOut);
        }

        if (useStillAgent)
        {
            stillAgentHeuristic(actionsOut);
        }
        //Used for human input
        else
        {
            var contActionsOut = actionsOut.ContinuousActions;
            contActionsOut[0] = input.moveInput.y;
            contActionsOut[1] = input.moveInput.x;
            contActionsOut[2] = input.rotateInput * 3; //rotate
            var discreteActionsOut = actionsOut.DiscreteActions;
            discreteActionsOut[0] = input.CheckIfInputSinceLastFrame(ref input.m_throwPressed) ? 1 : 0; //dash
            discreteActionsOut[1] = input.CheckIfInputSinceLastFrame(ref input.m_dashPressed) ? 1 : 0; //dash
        }
    }

    private void stillAgentHeuristic(in ActionBuffers actionsOut)
    {
        return;
    }
    private void RuleBasedHeuristic(in ActionBuffers actionsOut)
    {
        // Implement your custom rule-based logic to determine action values
        // Set the action values in the actionsOut.ActionSegment<float> variable


        // if (waypoints == null || waypoints.Count == 0)
        // {
        //     InitializeWaypoints();
        // }



        // Vector3 targetPosition = waypoints[currentWaypointIndex].position;
        MoveRuleBasedAgent(actionsOut);

        // // // Check distance from waypoint
        // // float distanceToWaypoint = Vector3.Distance(transform.position, targetPosition);
        // // Debug.Log($"Distance to waypoint {currentWaypointIndex}: {distanceToWaypoint}");

        // if (Vector3.Distance(transform.position, targetPosition) < waypointReachDistance)
        // {
        //     ShuffleWayPoints();
        //     currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.Count;
        // }
    }

    private void InitializeWaypoints()
    {
        // Code to initialize the waypoints list
        waypoints = new List<Transform>();
        for (int i = 0; i < waypointsContainer.childCount; i++)
        {
            waypoints.Add(waypointsContainer.GetChild(i));
        }
    }

    private void ShuffleWayPoints()
    {
        // Shuffle the waypoints list
        int waypointsCount = waypoints.Count;
        for (int i = 0; i < waypointsCount - 1; i++)
        {
            int randomIndex = UnityEngine.Random.Range(i, waypointsCount);
            Transform temp = waypoints[i];
            waypoints[i] = waypoints[randomIndex];
            waypoints[randomIndex] = temp;
        }
    }

    private Vector3 DetectEnemyPlayerForRotation(Vector3 direction, float detectionRadius)
    {
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius);
        Vector3 rotationDirection = direction;

        foreach (Collider hitCollider in hitColliders)
        {
            if (hitCollider.CompareTag("blueAgent") || hitCollider.CompareTag("blueAgentFront"))
            {
                rotationDirection = (hitCollider.transform.position - transform.position).normalized;
                break;
            }
        }

        return rotationDirection;
    }

    private (Vector3, Vector3) DetectBall(Vector3 targetDirection, float detectionRadius)
    {
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius);
        float minDistance = float.MaxValue;
        Vector3 closestBallDirection = targetDirection;
        Vector3 closestBallRotationDirection = targetDirection;

        foreach (Collider hitCollider in hitColliders)
        {
            if (hitCollider.CompareTag("dodgeBallPickup"))
            {
                float distanceToBall = Vector3.Distance(transform.position, hitCollider.transform.position);
                if (distanceToBall < minDistance)
                {
                    minDistance = distanceToBall;
                    closestBallDirection = (hitCollider.transform.position - transform.position).normalized;
                    closestBallRotationDirection = closestBallDirection;
                }
            }
        }

        return (closestBallDirection, closestBallRotationDirection);
    }


    private void MoveRuleBasedAgent(in ActionBuffers actionsOut)
    {

        if (Stunned)
        {
            return;
        }


        // OBSERVE
        // Agent
        RayPerceptionInput agent_spec = AgentRaycastSensor.GetRayPerceptionInput();
        RayPerceptionOutput agent_obs = RayPerceptionSensor.Perceive(agent_spec);
        // Back
        RayPerceptionInput back_spec = BackRaycastSensor.GetRayPerceptionInput();
        RayPerceptionOutput back_obs = RayPerceptionSensor.Perceive(back_spec);
        // Ball
        RayPerceptionInput ball_spec = BallRaycastSensor.GetRayPerceptionInput();
        RayPerceptionOutput ball_obs = RayPerceptionSensor.Perceive(ball_spec);
        // Wall
        RayPerceptionInput wall_spec = WallRaycastSensor.GetRayPerceptionInput();
        RayPerceptionOutput wall_obs = RayPerceptionSensor.Perceive(wall_spec);


        // DIV VARIABLES
        float max_length;
        float ball_interest;
        float bush_interest;
        Func<float, float> open_space_interest;
        float view_open_space_interest;
        float agent_interest;
        float agent_fear;
        float rotation_in_movement_direction;
        float previous_movement_interest;
        int n = 4;

        switch (fsm_version)
        {
            case 0:
                max_length = 50;
                ball_interest = (4 - currentNumberOfBalls) / 2;
                bush_interest = (float)0.3 * currentNumberOfBalls;
                open_space_interest = x => (float)1;
                view_open_space_interest = (float)0.5;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100 - (float)0.01;
                agent_fear = currentNumberOfBalls > 2 ? 0 : (float)0.1;
                rotation_in_movement_direction = (float)0.5;
                previous_movement_interest = (float)0.05;
                break;
            case 1:
                max_length = 50;
                ball_interest = (4 - currentNumberOfBalls) / 4;
                bush_interest = (float)0.7 * currentNumberOfBalls;
                open_space_interest = x => -(x - (float)0.15) * (x - (float)0.15) * (float)10;
                view_open_space_interest = (float)0.2;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100 - (float)0.01;
                agent_fear = currentNumberOfBalls > 2 ? 0 : (float)0.5;
                rotation_in_movement_direction = (float)0.4;
                previous_movement_interest = (float)0.5;
                n = 20;
                break;
            case 2:
                max_length = 50;
                ball_interest = Random.Range((float)0, (4 - currentNumberOfBalls) / 8);
                bush_interest = (float)1.5 + (float)0.4 * currentNumberOfBalls;
                open_space_interest = x => x < (float)0.05 ? -(float)0.3 : 0;
                view_open_space_interest = (float)0.01;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 200 - (float)0.01;
                agent_fear = currentNumberOfBalls > 2 ? (float)0.3 : (float)0.8;
                rotation_in_movement_direction = (float)0.4;
                previous_movement_interest = (float)0.9;
                n = 20;
                break;
            case 3:
                max_length = 50;
                ball_interest = (4 - currentNumberOfBalls) / 4;
                bush_interest = (float)0.4 * currentNumberOfBalls + (float)0.01;
                open_space_interest = x => (float)0; //-(x - (float)0.15) * (x - (float)0.15) * (float)10;
                view_open_space_interest = (float)0.6;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100 - (float)0.01;
                agent_fear = currentNumberOfBalls > 2 ? 0 : (float)0.5;
                rotation_in_movement_direction = (float)0.4;
                previous_movement_interest = (float)0.1;
                n = 20;

                break;
            case 4:
                max_length = 50;
                ball_interest = currentNumberOfBalls == 4 ? 0 : Mathf.Log(9, -currentNumberOfBalls + 5);
                bush_interest = (float)0.4 * currentNumberOfBalls + (float)0.2;
                open_space_interest = x => (float)0.01; //-(x - (float)0.15) * (x - (float)0.15) * (float)10;
                view_open_space_interest = (float)0.6;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100 - 0.01f;
                agent_fear = currentNumberOfBalls > 2 ? (float)0 : (float)0.5;
                rotation_in_movement_direction = 0;
                previous_movement_interest = 0;
                n = 20;

                break;
            case 5:
                max_length = 50;
                ball_interest = currentNumberOfBalls == 4 ? 0 : 0.4f - currentNumberOfBalls * 0.4f / 4; //Mathf.Log(1000000, -currentNumberOfBalls + 5) - currentNumberOfBalls * 0.02f;
                bush_interest = (float)0.1 * (4 - currentNumberOfBalls) + (float)0.2;
                open_space_interest = x => (float)0.01; //-(x - (float)0.15) * (x - (float)0.15) * (float)10;
                view_open_space_interest = (float)0.1;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100 - 0.01f;
                agent_fear = currentNumberOfBalls > 2 ? (float)0 : (float)0.2;
                rotation_in_movement_direction = 0;
                previous_movement_interest = 0;
                n = 20;

                break;
            default:
                max_length = 50;
                ball_interest = (4 - currentNumberOfBalls) / 2;
                bush_interest = (float)0.3 * currentNumberOfBalls;
                open_space_interest = x => (float)1;
                view_open_space_interest = (float)0.5;
                agent_interest = Mathf.Exp(currentNumberOfBalls) / 100;
                agent_fear = currentNumberOfBalls > 2 ? 0 : (float)0.1;
                rotation_in_movement_direction = (float)0.5;
                previous_movement_interest = (float)0.05;
                break;
        }



        // Initialize directories with angles from wall_spec and back_spec
        Dictionary<float, float> rotation_angles = new Dictionary<float, float>();
        Dictionary<float, float> movement_angles = new Dictionary<float, float>();

        foreach (float angle in wall_spec.Angles)
        {
            movement_angles[angle] = (float)0;
            rotation_angles[angle] = (float)0;
        }


        // NEW MOVEMENT AND ROTATION DIRECTION
        // Agent observations
        for (int i = 0; i < agent_spec.Angles.Count; i++)
        {
            // Movement away from agent front
            switch (agent_obs.RayOutputs[i].HitTagIndex)
            {
                case -1: // Not hit agent or hit something else
                    break;
                case 0: // Hit agent
                    break;
                case 1: // Hit agent front

                    // Want to try escape agent
                    float escape_angle1 = (agent_spec.Angles[i] + 90) % 360;
                    float escape_angle2 = (agent_spec.Angles[i] - 90) % 360;
                    float escape_variation = 20;
                    List<float> list_of_angles = movement_angles.Keys.ToList();
                    foreach (float angle in list_of_angles)
                    {
                        if (
                            (angle >= escape_angle1 - escape_variation && angle <= escape_angle1 + escape_variation) ||
                            (angle >= escape_angle2 - escape_variation && angle <= escape_angle2 + escape_variation)
                            )
                        {
                            movement_angles[angle] += agent_fear;
                        }
                    }
                    break;
            }

            // Rotation towards agent
            if (agent_obs.RayOutputs[i].HitTagIndex != -1) // Ray hit agent or agent front
            {
                if (rotation_angles.ContainsKey(agent_spec.Angles[i]))
                {
                    rotation_angles[agent_spec.Angles[i]] += agent_interest;
                }
            }
        }
        // Ball, bush and wall observations
        for (int i = 0; i < wall_spec.Angles.Count; i++)
        {
            // If observe ball
            movement_angles[ball_spec.Angles[i]] += ball_obs.RayOutputs[i].HitTagIndex == 1 ? (max_length - ball_obs.RayOutputs[i].HitFraction) / max_length * ball_interest : 0; // If HitTagIndex == 1 then the ball is available to be picked up

            // If observe wall/bush
            movement_angles[wall_spec.Angles[i]] += wall_obs.RayOutputs[i].HitTagIndex == 1 ? (max_length - wall_obs.RayOutputs[i].HitFraction) / max_length * bush_interest : wall_obs.RayOutputs[i].HitFraction / max_length * open_space_interest(wall_obs.RayOutputs[i].HitFraction);
            rotation_angles[wall_spec.Angles[i]] += wall_obs.RayOutputs[i].HitFraction * view_open_space_interest / max_length;

            // Prefer continue in same direction
            if (Math.Abs(previousMovementAngle - 90) < 0.0001 && Math.Abs(previousMovementAngle - wall_spec.Angles[i]) < 0.0001)
            {
                movement_angles[wall_spec.Angles[i]] += previous_movement_interest;
            }
            else
            {
                movement_angles[wall_spec.Angles[i]] += !(previousMovementAngle < 90 ^ wall_spec.Angles[i] < 90) ? previous_movement_interest : 0;
            }
        }


        // GET BEST ANGLE FOR MOVEMENT AND ROTATION
        float new_movement_angle = movement_angles.Aggregate((l, r) => l.Value > r.Value ? l : r).Key;

        IOrderedEnumerable<KeyValuePair<float, float>> sorted_movement = movement_angles.OrderByDescending(x => x.Value);
        // Get weighted random choice from the top n best
        // NEW MOVMENT DIRECTION
        float top_movment_sum = 0;
        for (int i = 0; i < n; i++)
        {
            top_movment_sum += sorted_movement.ElementAt(i).Value;
        }
        float random_movment_sum_value = Random.Range((float)0, top_movment_sum);
        float temp_sum = 0;
        for (int i = 0; i < n; i++)
        {
            temp_sum += sorted_movement.ElementAt(i).Value;
            if (random_movment_sum_value <= temp_sum)
            {
                new_movement_angle = sorted_movement.ElementAt(i).Key;
                break;
            }
        }


        rotation_angles[new_movement_angle] += rotation_in_movement_direction;
        float max_rotation_angle = rotation_angles.Aggregate((l, r) => l.Value > r.Value ? l : r).Key;

        // ROTATE AGENT
        float smoothRotation = Mathf.LerpAngle(transform.eulerAngles.y, transform.eulerAngles.y + max_rotation_angle + 90, Time.fixedDeltaTime * rotationSpeed);
        transform.rotation = Quaternion.Euler(0, smoothRotation, 0);

        // MOVE AGENT
        double z_delta = Math.Sin((new_movement_angle) * Math.PI / 180);
        double x_delta = Math.Cos((new_movement_angle) * Math.PI / 180);
        float eagerness = movement_angles[new_movement_angle] / 2 > 1 ? agentSpeed : (agentSpeed * 2 / 3) * (movement_angles[new_movement_angle] / 2) + agentSpeed / 3;
        var moveDir = transform.TransformDirection(new Vector3((float)x_delta * eagerness, 0, (float)z_delta * eagerness));
        m_CubeMovement.RunOnGround(moveDir);
    }

    void Update()
    {
        if (true)
        {
            myCurrentObjectRect = EyeLinkWebLinkUtil.getScreenRectFromGameObject(thisObject);

            if (myCurrentObjectRect != myPreviousObjectRect)
            {
                currentUpdateTime = (int)Math.Round(Time.realtimeSinceStartup * 1000 + EyeLinkWebLinkUtil.timeOffset);
                if (haveStarted == 1)
                {
                    ttW = Convert.ToString(EyeLinkWebLinkUtil.iasZeroPoint - previousUpdateTime) + " " + Convert.ToString(EyeLinkWebLinkUtil.iasZeroPoint - currentUpdateTime) +
                          " !V IAREA RECTANGLE 1 " + Convert.ToString(myPreviousObjectRect.xMin - 25) + " " + Convert.ToString(myPreviousObjectRect.yMin - 25) +
                          " " + Convert.ToString(myPreviousObjectRect.xMax + 25) + " " + Convert.ToString(myPreviousObjectRect.yMax + 25) + " enemy";
                    EyeLinkWebLinkUtil.writeIASLine(ttW);

                }
                myPreviousObjectRect = myCurrentObjectRect;
                previousUpdateTime = currentUpdateTime;

                if (haveStarted == 0)
                {
                    haveStarted = 1;
                }
            }
        }
    }
}
